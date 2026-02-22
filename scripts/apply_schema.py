from __future__ import annotations

from nta.graph.db import Neo4jConfig
from nta.graph.db import apply_schema
from nta.graph.db import get_driver


def main() -> None:
    config = Neo4jConfig.from_env()

    driver = get_driver(config)
    try:
        apply_schema(driver)
    finally:
        driver.close()

    print("Neo4j schema applied.")


if __name__ == "__main__":
    main()
