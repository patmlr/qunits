"""
Generates the generated parts of the qunits website with qdocs (https://github.com/patmlr/qdocs). Run from anywhere:

    python docs/_gen/build.py [api | tutorials | logo | all]

- api: the API pages in docs/doc/functions/ and the navigation docs/_includes/api-nav.html.
- tutorials: the highlighted code blocks docs/_includes/code/*.html from the marked regions in examples/*.py.
- logo: the dark mode logo docs/assets/img/logo_dark.svg from logo.svg.
"""

import os

from qdocs import Project, main

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

PROJECT = Project(
    package="qunits",
    modules=["dimension", "prefix", "registry", "unit"],
    root=ROOT,
    namespaced={"dimension", "prefix"},
    namespaces={"qunits.u"},
)


if __name__ == "__main__":
    main(PROJECT)
