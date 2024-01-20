#! /usr/bin/env python3
import argparse

from redist_project import creategpkg


def progress(count=0, total=0, msg=None):
    if msg:
        print(msg)

    if total:
        pct = int(100 * count / total)
        prog = f'[{"*" * int(20 * count/total):20}] {pct}%'
        print(prog, end=("\n" if pct == 100 else "\r"))


states = ['ak', 'al', 'ar', 'az', 'ca', 'co', 'ct', 'dc', 'de', 'fl', 'ga',
          'hi', 'ia', 'id', 'il', 'in', 'ks', 'ky', 'la', 'ma', 'md', 'me',
          'mi', 'mn', 'mo', 'ms', 'mt', 'nc', 'nd', 'ne', 'nh', 'nj', 'nm',
          'nv', 'ny', 'oh', 'ok', 'or', 'pa', 'ri', 'sc', 'sd', 'tn', 'tx',
          'ut', 'va', 'vt', 'wa', 'wi', 'wv', 'wy']

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='importdata',
        description='Import PL data as provided by Redistricting Data Hub'
    )
    parser.add_argument('input_dir', help='Directory with RDH files to import')
    parser.add_argument(
        'output_gpkg', help='Path to GeoPackage file to create')
    parser.add_argument('-s', '--state', choices=states,
                        required=True, help="Two-letter state code. Required.")
    parser.add_argument('-y', '--year', default="2020",
                        help="Decennial census year to import. Default is 2020.")
    parser.add_argument('-a', '--acs-year', default="2021",
                        help="American Community Survey 5-year year to import. Default is 2021")
    parser.add_argument('-r', '--voter-file-date',
                        help="Date of voter file to import. Optional.")

    args = parser.parse_args()

    src_path = args.input_dir
    gpkg = args.output_gpkg
    st_prefix = args.state
    dec_year = args.year
    acs_year = args.acs_year
    vr_date = args.voter_file_date

    with creategpkg.GeoPackageCreator(st_prefix, gpkg, src_path, progress) as imp:
        imp.import_decennial(dec_year, acs_year, vr_date)
