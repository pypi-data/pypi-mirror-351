from uuid import UUID
from mumle.concrete_syntax.textual_od import parser, renderer
from mumle.concrete_syntax.common import indent

# Clones an object diagram
def clone_od(state, m: UUID, mm: UUID):
    # cheap-ass implementation: render and parse
    cs = renderer.render_od(state, m, mm, hide_names=False)
    return parser.parse_od(state, cs, mm)
