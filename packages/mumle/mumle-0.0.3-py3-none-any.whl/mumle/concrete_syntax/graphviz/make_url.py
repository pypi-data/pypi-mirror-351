from mumle.concrete_syntax.common import indent
import urllib.parse
import webbrowser

def make_url(graphviz_txt: str, engine="dot") -> str:

    as_digraph = f"digraph {{\n{indent(graphviz_txt, 2)}\n}}"

    # This one seems much faster:
    return f"https://edotor.net/?engine={engine}#{urllib.parse.quote(as_digraph)}"

    # Keeping this one here just in case:
    # return "https://dreampuf.github.io/GraphvizOnline/#"+urllib.parse.quote(graphviz)


def show_graphviz(graphviz_txt: str, engine="dot"):
    return webbrowser.open(make_url(graphviz_txt, engine))
