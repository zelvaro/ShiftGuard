"""Extraction structurée du profil candidat et scoring."""

from app.schemas.candidate import CandidateExtraction

SYSTEM_PROMPT = """Tu analyses les messages d'un candidat à un poste d'agent de sécurité au Maroc.
Les messages peuvent être en darija, français ou arabe. Réponds uniquement en JSON
conforme au schéma fourni. N'invente rien : laisse null ce qui n'est pas dit."""


async def extract_candidate(text: str) -> CandidateExtraction:
    # TODO : appeler le LLM avec SYSTEM_PROMPT + text et valider la sortie avec Pydantic.
    raise NotImplementedError


def score_candidate(c: CandidateExtraction) -> int:
    """Score simple et explicable (0-100), à affiner avec les clients."""
    score = 0
    if c.has_pro_card:
        score += 35
    if c.experience_years:
        score += min(int(c.experience_years * 10), 30)
    if c.availability:
        score += 15
    if c.city:
        score += 10
    if c.full_name:
        score += 10
    return min(score, 100)
