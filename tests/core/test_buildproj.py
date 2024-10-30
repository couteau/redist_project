from redist_project.core.buildproj import load_styles


class TestBuildProj:
    def test_load_styles(self):
        styles = load_styles()
        assert len(styles) == 7
