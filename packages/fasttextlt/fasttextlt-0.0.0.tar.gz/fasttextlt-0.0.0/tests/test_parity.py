import pathlib

import numpy as np
from numpy.testing import assert_equal
import fasttext
from hypothesis import given, strategies as st

from fasttextlt.fasttext import FastText as FastTextLt
from fasttextlt.format import load


def test_load_parity(model_path: pathlib.Path):
    ft_model = fasttext.load_model(str(model_path))
    with open(model_path, "rb") as in_stream:
        ftlt_model = load(in_stream, full_model=True)

    for i, word in enumerate(ftlt_model.raw_vocab):
        assert ft_model.get_word_id(word) == i

    # FIXME: can we save memory here somehow?

    ft_input_matrix = np.array(ft_model.f.getInputMatrix(), copy=False)
    ftlt_input_matrix = ftlt_model.vectors_ngrams
    assert_equal(ftlt_input_matrix, ft_input_matrix)

    ft_output_matrix = np.array(ft_model.f.getOutputMatrix(), copy=False)
    ftlt_output_matrix = ftlt_model.hidden_output
    assert_equal(ftlt_output_matrix, ft_output_matrix)


@given(
    word=st.text(
        alphabet=st.characters(
            blacklist_categories=["Cs", "Zs"],
            blacklist_characters=[
                "\t",
                "\n",
                "\r",
                "\N{LINE TABULATION}",
                "\N{FORM FEED}",
                "\N{FILE SEPARATOR}",
                "\N{GROUP SEPARATOR}",
                "\N{RECORD SEPARATOR}",
                "\N{NEXT LINE}",
                "\N{LINE SEPARATOR}",
                "\N{PARAGRAPH SEPARATOR}",
            ],
        ),
        min_size=1,
    )
)
def test_subwords_parity(models: tuple[FastTextLt, fasttext.FastText._FastText], word: str):
    ftlt_model, ft_model = models
    ft_ngrams, ft_subword_ids = ft_model.get_subwords(word)
    # FIXME: support computing ngrams, then test ngrams
    subword_ids = ftlt_model.get_subword_ids(word)
    assert_equal(ft_subword_ids, subword_ids)
