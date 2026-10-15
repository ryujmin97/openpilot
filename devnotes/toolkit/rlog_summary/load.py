import capnp, zstandard, sys, collections, os
SCHEMA = os.environ.get('SCHEMA_DIR', './schema')  # 로그를 기록한 커밋의 cereal + car.capnp 폴더
capnp.remove_import_hook()
log = capnp.load(os.path.join(SCHEMA,'log.capnp'), imports=[SCHEMA])
def events(path):
    data = zstandard.ZstdDecompressor().stream_reader(open(path,'rb')).read()
    return log.Event.read_multiple_bytes(data)
if __name__=='__main__':
    c = collections.Counter()
    for e in events(sys.argv[1]):
        c[e.which()] += 1
    for k,v in c.most_common(40): print(k,v)
