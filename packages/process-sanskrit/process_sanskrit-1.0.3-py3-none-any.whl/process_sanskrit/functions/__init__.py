# Import main functions to expose at the module level
from process_sanskrit.functions.process import process
from process_sanskrit.functions.dictionaryLookup import dict_search, multidict
from process_sanskrit.functions.rootAnyWord import root_any_word
from process_sanskrit.functions.hybridSplitter import hybrid_sandhi_splitter
from process_sanskrit.functions.inflect import inflect
from process_sanskrit.functions.cleanResults import clean_results
from process_sanskrit.functions.compoundAnalysis import root_compounds, process_root_result
