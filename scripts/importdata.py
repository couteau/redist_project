import sys

from redist_project import creategpkg


def progress(count=0, total=0, msg=None):
    if msg:
        print(msg)

    if total:
        pct = int(100 * count / total)
        prog = f'[{"*" * int(20 * count/total):20}] {pct}%'
        print(prog, end=("\n" if pct == 100 else "\r"))


if __name__ == '__main__':
    st_prefix = sys.argv[1]
    gpkg = sys.argv[2]
    shp_path = sys.argv[3]

    creategpkg.import_state(st_prefix, gpkg, shp_path, progress=progress)
