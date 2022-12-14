from uspto_rejections_kayal_pillay import uspto_rejections_kayal_pillay
from uspto_rejections_kayal_pillay import __version__

import pytest

#test package version for use
def test_version():
    assert __version__ == '0.1.0'

#test to ensure assert isinstance as str or int (as case may be) works
with pytest.raises(AssertionError):
  all_patents(99)
  year_seperator(99)
  patent_reject("14983812")
  rejection_filter('headerMissing')
  rejection_graph('headerMissing')
  type_rejections_crosstab(2020)
  type_rejections_overall(99)
  actiontype_bycategory("allow")
  actiontype_clean(900)

#test to ensure that actiontype_clean function is working
def actiontype_clean_test():
    examples = [("Rejected", "reject", "Rejected"), ("Withdrawn", "withdrawal", "Withdrawn"), ("Cancelled", "cancel", "Cancelled")]
    for (category, example, expected) in examples:
        df = actiontype_clean()
        filtered = df[df['actionTypeCategory'] == category]
        actual = filtered.unique()
    assert actual == expected
    
    print("Passed regex test.")