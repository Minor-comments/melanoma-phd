from typing import List, MutableMapping, Optional

from plotly.express.colors import sample_colorscale


class ColorGenerator:
    def __init__(self, color_cache: Optional[MutableMapping] = None):
        self._cache = color_cache

    def generate(self, variable_names: List[str]) -> List[str]:
        colorscale = self.__get_colorscale(variable_names)
        sample_colors = sample_colorscale(
            colorscale,
            [(1 / len(variable_names) * (i + 1)) for i in range(len(variable_names))],
        )
        cache_key = "-".join(sorted(variable_names))
        if self._cache and cache_key in self._cache:
            sample_colors = self._cache[cache_key]
        return sample_colors

    def __get_colorscale(self, distribution_variable_names: List[str]) -> str:
        colorscale_dict = {
            "Magenta": ["naive", "mem central", "mem efectora", "efectora", "transitional"],
            "Burgyl": ["CD4", "CD8", "DN", "DP"],
            "Blugrn": ["LT", "LB", "NK"],
        }
        default = "Plotly3"
        for colorscale, variable_substrings in colorscale_dict.items():
            for variable_substring in variable_substrings:
                for distribution_variable_name in distribution_variable_names:
                    if variable_substring in distribution_variable_name:
                        return colorscale
        return default
