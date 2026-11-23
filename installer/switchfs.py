"""Minimal read-only Nintendo Switch container reader.

Supports what the installer needs: NSP (PFS0) -> NCA (NCA3, AES-CTR / AES-CTR-EX)
-> RomFS, including update NCAs that patch a base NCA (BKTR / indirect storage).
Keys come from the user's own prod.keys (e.g. the one their emulator uses).
"""
import bisect
import re
import struct

from Crypto.Cipher import AES
from Crypto.Util import Counter
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


# ---------------------------------------------------------------- keys / tickets
def load_keys(path):
    text = open(path, encoding='utf-8', errors='replace').read()
    return {k.lower(): bytes.fromhex(v)
            for k, v in re.findall(r'^\s*(\w+)\s*=\s*([0-9a-fA-F]+)\s*$', text, re.M)
            if len(v) % 2 == 0}


def ticket_titlekey(keys, tik_bytes):
    """Decrypt the common-ticket title key. Returns (rights_id_hex, titlekey)."""
    enc = tik_bytes[0x180:0x190]
    rights_id = tik_bytes[0x2a0:0x2b0]
    gen = rights_id[15]
    kek_name = 'titlekek_%02x' % max(gen - 1, 0)
    if kek_name not in keys:
        raise KeyError(f'{kek_name} missing from prod.keys (update your keys)')
    return rights_id.hex(), AES.new(keys[kek_name], AES.MODE_ECB).decrypt(enc)


# ---------------------------------------------------------------- PFS0 (NSP)
class Pfs0:
    def __init__(self, path):
        self.f = open(path, 'rb')
        hdr = self.f.read(0x10)
        if hdr[:4] != b'PFS0':
            raise ValueError(f'{path}: not an NSP/PFS0 file')
        n, strsize = struct.unpack_from('<II', hdr, 4)
        entries = self.f.read(0x18 * n)
        strtab = self.f.read(strsize)
        data_start = 0x10 + 0x18 * n + strsize
        self.files = {}
        for i in range(n):
            off, size, name_off = struct.unpack_from('<QQI', entries, i * 0x18)
            name = strtab[name_off:strtab.index(b'\0', name_off)].decode()
            self.files[name] = (data_start + off, size)

    def read(self, name):
        off, size = self.files[name]
        self.f.seek(off)
        return self.f.read(size)


class SubFile:
    """File-like window into a container (NCA inside an NSP)."""
    def __init__(self, f, off, size):
        self.f, self.off, self.size = f, off, size

    def read_at(self, pos, size):
        self.f.seek(self.off + pos)
        return self.f.read(size)


class MultiPartFile:
    """A plain file, or an emulator-NAND split NCA (a folder containing 00, 01, ...)."""
    def __init__(self, path):
        import os
        if os.path.isdir(path):
            names = sorted(n for n in os.listdir(path) if n.isdigit())
            parts = [os.path.join(path, n) for n in names]
        else:
            parts = [path]
        self.parts = []
        pos = 0
        for p in parts:
            size = os.path.getsize(p)
            self.parts.append((pos, size, open(p, 'rb')))
            pos += size
        self.size = pos

    def read_at(self, pos, size):
        out = bytearray()
        for start, psize, f in self.parts:
            if size <= 0:
                break
            if start <= pos < start + psize:
                n = min(size, start + psize - pos)
                f.seek(pos - start)
                out += f.read(n)
                pos += n
                size -= n
        return bytes(out)


def load_title_keys(paths, keys):
    """Read title.keys-style files ("rightsid = key"). Returns {rights_id: [candidate decrypted keys]}.

    Emulator-generated files hold the ticket's (encrypted) key, user dumps usually hold the
    decrypted key - both interpretations are returned and verified later against the NCA.
    """
    out = {}
    for p in paths:
        try:
            text = open(p, encoding='utf-8', errors='replace').read()
        except OSError:
            continue
        for rid, val in re.findall(r'^\s*([0-9a-fA-F]{32})\s*=\s*([0-9a-fA-F]{32})\s*$', text, re.M):
            rid = rid.lower()
            raw = bytes.fromhex(val)
            cands = out.setdefault(rid, [])
            kek = keys.get('titlekek_%02x' % max(int(rid[-2:], 16) - 1, 0))
            if kek:
                cands.append(AES.new(kek, AES.MODE_ECB).decrypt(raw))
            cands.append(raw)
    return out


# ---------------------------------------------------------------- NCA
def _xts_decrypt(key, data, sector_size=0x200):
    out = bytearray()
    for i in range(0, len(data), sector_size):
        tweak = (i // sector_size).to_bytes(16, 'big')
        d = Cipher(algorithms.AES(key), modes.XTS(tweak)).decryptor()
        out += d.update(data[i:i + sector_size]) + d.finalize()
    return bytes(out)


def _ctr(key, upper8, off, data, generation=None):
    iv = upper8 if generation is None else upper8[:4] + struct.pack('>I', generation)
    ctr = int.from_bytes(iv + struct.pack('>Q', off >> 4), 'big')
    return AES.new(key, AES.MODE_CTR, counter=Counter.new(128, initial_value=ctr)).decrypt(data)


class Nca:
    CONTENT_PROGRAM = 0

    def __init__(self, sub, keys):
        self.sub = sub
        hdr = _xts_decrypt(keys['header_key'], sub.read_at(0, 0xC00))
        if hdr[0x200:0x204] != b'NCA3':
            raise ValueError('unsupported NCA (expected NCA3; check header_key)')
        self.hdr = hdr
        self.content_type = hdr[0x205]
        self.title_id = struct.unpack_from('<Q', hdr, 0x210)[0]
        self.rights_id = hdr[0x230:0x240].hex()
        self.key = None
        self.sections = []
        for i in range(4):
            s, e = struct.unpack_from('<II', hdr, 0x240 + i * 0x10)
            self.sections.append((s * 0x200, e * 0x200, hdr[0x400 + i * 0x200:0x600 + i * 0x200]))

    @property
    def is_update(self):
        """True if the RomFS section is a patch (BKTR) over a base NCA."""
        return self.sections[1][2][0x110:0x114] == b'BKTR'

    def key_works(self, key):
        """Verify a title key by decrypting the ExeFS (section 0) PFS0 magic."""
        start, end, fsh = self.sections[0]
        if end == 0 or fsh[3] != 2:  # needs HierarchicalSha256 ExeFS
            return False
        layer_count = struct.unpack_from('<I', fsh, 0x8 + 0x24)[0]
        pfs_off = struct.unpack_from('<Q', fsh, 0x8 + 0x28 + (layer_count - 1) * 0x10)[0]
        old = self.key
        self.key = key
        try:
            return Section(self, 0).read(pfs_off, 4) == b'PFS0'
        finally:
            self.key = old

    def set_key(self, candidates):
        for k in candidates:
            if self.key_works(k):
                self.key = k
                return True
        return False


class Section:
    def __init__(self, nca, idx):
        self.nca = nca
        self.start, self.end, self.fsh = nca.sections[idx]
        self.upper = self.fsh[0x140:0x148][::-1]

    def read(self, off, size, generation=None):
        a = off & ~0xF
        b = (off + size + 0xF) & ~0xF
        data = self.nca.sub.read_at(self.start + a, b - a)
        dec = _ctr(self.nca.key, self.upper, self.start + a, data, generation)
        return dec[off - a:off - a + size]


def _bucket_entries(raw, entry_size, count, fmt):
    node = 0x4000
    per_set = (node - 0x10) // entry_size
    nsets = (count + per_set - 1) // per_set
    if nsets > (node - 0x10) // 8:
        raise NotImplementedError('bucket trees with L2 nodes are not supported')
    out = []
    end = 0
    for s in range(nsets):
        base = node * (1 + s)
        _, cnt, end = struct.unpack_from('<iiq', raw, base)
        out += [struct.unpack_from(fmt, raw, base + 0x10 + j * entry_size) for j in range(cnt)]
    return out, end


class PatchedRomfsStorage:
    """Virtual RomFS image of an update NCA section patched over its base section."""
    def __init__(self, base_sec, upd_sec):
        self.b, self.u = base_sec, upd_sec
        pi = upd_sec.fsh[0x100:0x140]
        if pi[0x10:0x14] != b'BKTR' or pi[0x30:0x34] != b'BKTR':
            raise ValueError('update NCA has no patch (BKTR) info')
        ind_off, ind_size = struct.unpack_from('<QQ', pi, 0)
        ind_cnt = struct.unpack_from('<I', pi, 0x18)[0]
        aes_off, aes_size = struct.unpack_from('<QQ', pi, 0x20)
        aes_cnt = struct.unpack_from('<I', pi, 0x38)[0]
        aes, _ = _bucket_entries(upd_sec.read(aes_off, aes_size), 0x10, aes_cnt, '<QB3xI')
        self.aes = [(o, g) for o, _, g in aes]
        self.aes_o = [o for o, _ in self.aes]
        self.aes_end = aes_off
        self.ind, self.vsize = _bucket_entries(self._read_patch(ind_off, ind_size), 0x14, ind_cnt, '<QQi')
        self.ind_v = [e[0] for e in self.ind]

    def _read_patch(self, off, size):
        out = bytearray()
        while size > 0:
            i = bisect.bisect_right(self.aes_o, off) - 1
            o, g = self.aes[i]
            nxt = self.aes_o[i + 1] if i + 1 < len(self.aes) else self.aes_end
            n = min(size, nxt - off)
            out += self.u.read(off, n, generation=g)
            off += n
            size -= n
        return bytes(out)

    def read(self, off, size):
        out = bytearray()
        while size > 0:
            i = bisect.bisect_right(self.ind_v, off) - 1
            v, p, storage = self.ind[i]
            nxt = self.ind_v[i + 1] if i + 1 < len(self.ind) else self.vsize
            n = min(size, nxt - off)
            po = p + (off - v)
            out += self.b.read(po, n) if storage == 0 else self._read_patch(po, n)
            off += n
            size -= n
        return bytes(out)


# ---------------------------------------------------------------- RomFS
class Romfs:
    def __init__(self, read, fsh):
        self.read = read
        hd = fsh[0x8:0x100]
        if hd[:4] != b'IVFC':
            raise ValueError('RomFS section has no IVFC header')
        nlev = struct.unpack_from('<I', hd, 0xC)[0]
        self.data_off = struct.unpack_from('<Q', hd, 0x10 + (nlev - 2) * 0x18)[0]
        h = struct.unpack_from('<10Q', read(self.data_off, 0x50))
        self.dmeta = read(self.data_off + h[3], h[4])
        self.fmeta = read(self.data_off + h[7], h[8])
        self.fdata = self.data_off + h[9]
        self.files = {}
        self._walk(0, '')

    def _walk(self, doff, path):
        _, _, child, ffile, _, nlen = struct.unpack_from('<IIIIII', self.dmeta, doff)
        name = self.dmeta[doff + 0x18:doff + 0x18 + nlen].decode()
        p = '' if doff == 0 else path + name + '/'
        f = ffile
        while f != 0xFFFFFFFF:
            _, sib, foff, fsize, _, fnlen = struct.unpack_from('<IIQQII', self.fmeta, f)
            fname = self.fmeta[f + 0x20:f + 0x20 + fnlen].decode()
            self.files[p + fname] = (self.fdata + foff, fsize)
            f = sib
        c = child
        while c != 0xFFFFFFFF:
            self._walk(c, p)
            c = struct.unpack_from('<I', self.dmeta, c + 4)[0]

    def extract(self, name, dst, chunk=16 << 20):
        off, size = self.files[name]
        with open(dst, 'wb') as fo:
            pos = 0
            while pos < size:
                n = min(chunk, size - pos)
                fo.write(self.read(off + pos, n))
                pos += n


# ---------------------------------------------------------------- high level
def program_ncas_in_nsp(nsp_path, keys):
    """Yield (Nca, {rights_id: [titlekey]}) for each Program NCA inside an NSP."""
    pfs = Pfs0(nsp_path)
    tkeys = {}
    for name in pfs.files:
        if name.endswith('.tik'):
            rid, tk = ticket_titlekey(keys, pfs.read(name))
            tkeys.setdefault(rid, []).append(tk)
    for name, (off, size) in pfs.files.items():
        if name.endswith('.nca') and not name.endswith('.cnmt.nca'):
            nca = Nca(SubFile(pfs.f, off, size), keys)
            if nca.content_type == Nca.CONTENT_PROGRAM:
                yield nca, tkeys


def apply_title_key(nca, *key_tables):
    if not nca.rights_id.strip('0'):
        raise NotImplementedError('NCAs without a rights ID (key-area encryption) are not supported')
    cands = [k for table in key_tables for k in table.get(nca.rights_id, [])]
    return nca.set_key(cands)


def open_patched_romfs_ncas(base, upd):
    bs, us = Section(base, 1), Section(upd, 1)
    return Romfs(PatchedRomfsStorage(bs, us).read, us.fsh)
