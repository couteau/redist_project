import pandas as pd

from .state import states

assignments = {
    'place': 'INCPLACE_CDP',
    'aiannh': 'AIANNH',
}


def join_assignments(st, dec_year, df, src_path):
    baf = []
    for geog in assignments:
        fn = f"BlockAssign_ST{states[st].fips}_{st.upper()}_{assignments[geog]}.txt"
        p = src_path / "baf" / fn
        baf.append(pd.read_csv(p, header=0, delimiter='|', index_col='BLOCKID'))

    return df.join(baf)
