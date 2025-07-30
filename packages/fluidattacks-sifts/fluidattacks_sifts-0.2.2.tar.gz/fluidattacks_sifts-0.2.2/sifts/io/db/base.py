from sifts.common_types.snippets import Snippet, Vulnerability


class AnalysisDB:
    async def get_vulnerability(self, pk: str, sk: str) -> Vulnerability | None:
        msg = "Method get_vulnerability not implemented"
        raise NotImplementedError(msg)

    async def insert_vulnerability(self, vuln: Vulnerability) -> bool:
        msg = "Method insert_vulnerability not implemented"
        raise NotImplementedError(msg)

    async def insert_snippet(self, snippet: Snippet) -> bool:
        msg = "Method insert_snippet not implemented"
        raise NotImplementedError(msg)

    async def get_snippet(self, pk: str, sk: str) -> Snippet | None:
        msg = "Method get_snippet not implemented"
        raise NotImplementedError(msg)

    async def get_vulnerabilities_by_snippet(
        self,
        root_id: str,
        path: str,
        snippet_hash: str,
    ) -> list[Vulnerability]:
        msg = "Method get_vulnerabilities_by_snippet not implemented"
        raise NotImplementedError(msg)

    async def get_vulnerabilities_vulnerable(self) -> list[Vulnerability]:
        msg = "Method get_vulnerabilities_vulnerable not implemented"
        raise NotImplementedError(msg)
