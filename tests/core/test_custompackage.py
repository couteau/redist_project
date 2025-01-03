import pathlib

from pytest_mock import MockerFixture

import redist_project.core.buildpkg
from redist_project.core.buildpkg import build_geopackage
from redist_project.datapkg.bef import EquivalencyData


class TestCreatePackage:

    def test_build_geopackage(self, datadir: pathlib.Path, state_list_2020, mocker: MockerFixture):
        settings = mocker.patch.object(redist_project.core.buildpkg, "settings")
        settings.datapath = datadir

        build_geopackage(
            state_list_2020['ri'],
            "2020",
            "2021",
            None,
            vr_path=datadir / 'RI_l2_2020block_agg_20210902.csv',
            addl_bef=[EquivalencyData(
                datadir / 'ri_dhc_2020_b.csv',
                'GEOID20',
                {
                    "URBAN": "urban",
                    "RURAL": "rural",
                    "NOT_DEF": "not_def",
                    "MED_AGE": "med_age",
                    "MED_AGE_M": "med_age_m",
                    "MED_AGE_F": "med_age_f",
                    "MALE": "male",
                    "U5_M": "age_u5_m",
                    "5_9_M": "age_5_9_m",
                    "10_14_M": "age_10_14_m",
                    "15_17_M": "age_15_17_m",
                    "18_19_M": "age_18_19_m",
                    "20_M": "age_20_m",
                    "21_M": "age_21_m",
                    "22_24_M": "age_22_24_m",
                    "25_29_M": "age_25_29_m",
                    "30_34_M": "age_30_34_m",
                    "35_39_M": "age_35_39_m",
                    "40_44_M": "age_40_44_m",
                    "45_49_M": "age_45_49_m",
                    "50_54_M": "age_50_54_m",
                    "55_59_M": "age_55_59_m",
                    "60_61_M": "age_60_61_m",
                    "62_64_M": "age_62_64_m",
                    "65_66_M": "age_65_66_m",
                    "67_69_M": "age_67_69_m",
                    "70_74_M": "age_70_74_m",
                    "75_79_M": "age_75_79_m",
                    "80_84_M": "age_80_84_m",
                    "85_O_M": "age_85_o_m",
                    "FEMALE": "female",
                    "U5_F": "u5_f",
                    "5_9_F": "age_5_9_f",
                    "10_14_F": "age_10_14_f",
                    "15_17_F": "age_15_17_f",
                    "18_19_F": "age_18_19_f",
                    "20_F": "age_20_f",
                    "21_F": "age_21_f",
                    "22_24_F": "age_22_24_f",
                    "25_29_F": "age_25_29_f",
                    "30_34_F": "age_30_34_f",
                    "35_39_F": "age_35_39_f",
                    "40_44_F": "age_40_44_f",
                    "45_49_F": "age_45_49_f",
                    "50_54_F": "age_50_54_f",
                    "55_59_F": "age_55_59_f",
                    "60_61_F": "age_60_61_f",
                    "62_64_F": "age_62_64_f",
                    "65_66_F": "age_65_66_f",
                    "67_69_F": "age_67_69_f",
                    "70_74_F": "age_70_74_f",
                    "75_79_F": "age_75_79_f",
                    "80_84_F": "age_80_84_f",
                    "85_O_F": "age_85_o_f",
                    "IN_HH_POP": "in_hh_pop",
                    "HH_IN_HH": "hh_in_hh",
                    "M_HH": "m_hh",
                    "M_ALONE": "m_alone",
                    "M_N_ALONE": "m_n_alone",
                    "F_HH": "f_hh",
                    "F_ALONE": "f_alone",
                    "F_N_ALONE": "f_n_alone",
                    "O_SEX_MAR": "o_sex_mar",
                    "S_SEX_MAR": "s_sex_mar",
                    "O_SEX_UMAR": "o_sex_umar",
                    "S_SEX_UMAR": "s_sex_umar",
                    "BIO_CHLD": "bio_chld",
                    "BIO_U18": "bio_u18",
                    "ADPT_CHLD": "adpt_chld",
                    "ADPT_U18": "adpt_u18",
                    "STEP_CHLD": "step_chld",
                    "STEP_U18": "step_u18",
                    "GRAND_CHLD": "grand_chld",
                    "GRAND_U18": "grand_u18",
                    "SIBLING": "sibling",
                    "PARENT": "parent",
                    "PAR_INLAW": "par_inlaw",
                    "CHLD_INLAW": "chld_inlaw",
                    "OTH_REL": "oth_rel",
                    "FSTR_CHLD": "fstr_chld",
                    "OTH_NONREL": "oth_nonrel",
                    "GRP_QUART": "grp_quart",
                    "GRP_INST": "grp_inst",
                    "GRP_N_INST": "grp_n_inst"
                }
            )],
            addl_shp={
                "urban_areas": str(datadir / "Urban_Areas_4879541579459676182.zip")
            }
        )
