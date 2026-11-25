"""Layer 2 (18-item Trait Assessment) and Layer 3 (Adaptive Skill Prompt) definitions."""

LAYER2_TRAIT_QUESTIONS: dict[str, list[dict[str, str]]] = {
    "analytical": [
        {
            "id": "AN-1",
            "dimension": "Interest",
            "prompt": "I enjoy solving math problems, logic puzzles, or scientific mysteries.",
        },
        {
            "id": "AN-2",
            "dimension": "Ability",
            "prompt": "I can analyze numbers, lab observations, or evidence to draw a logical conclusion.",
        },
        {
            "id": "AN-3",
            "dimension": "Subject Preference",
            "prompt": "I enjoy and perform well in Mathematics, Statistics, or Science subjects.",
        },
    ],
    "creative": [
        {
            "id": "CR-1",
            "dimension": "Interest",
            "prompt": "I enjoy creating original designs, artwork, stories, or digital media.",
        },
        {
            "id": "CR-2",
            "dimension": "Ability",
            "prompt": "I am good at coming up with fresh ideas to improve how something looks or communicates.",
        },
        {
            "id": "CR-3",
            "dimension": "Subject Preference",
            "prompt": "I enjoy and perform well in Arts, Literature, Media, or Communication subjects.",
        },
    ],
    "technical": [
        {
            "id": "TE-1",
            "dimension": "Interest",
            "prompt": "I enjoy working with computers, laboratory tools, machinery, or hands-on equipment.",
        },
        {
            "id": "TE-2",
            "dimension": "Ability",
            "prompt": "I can quickly learn how to operate, build, or troubleshoot technical devices and tools.",
        },
        {
            "id": "TE-3",
            "dimension": "Subject Preference",
            "prompt": "I enjoy and perform well in ICT, Computer Systems, Lab Work, or TVL/Technical subjects.",
        },
    ],
    "people": [
        {
            "id": "PE-1",
            "dimension": "Interest",
            "prompt": "I enjoy helping, caring for, teaching, or guiding other people.",
        },
        {
            "id": "PE-2",
            "dimension": "Ability",
            "prompt": "I communicate clearly and collaborate well with others to support their needs or solve conflicts.",
        },
        {
            "id": "PE-3",
            "dimension": "Subject Preference",
            "prompt": "I enjoy and perform well in Social Sciences, Oral Communication, or group-based class activities.",
        },
    ],
    "organizational": [
        {
            "id": "OR-1",
            "dimension": "Interest",
            "prompt": "I enjoy planning schedules, organizing files, and following structured step-by-step rules.",
        },
        {
            "id": "OR-2",
            "dimension": "Ability",
            "prompt": "I pay close attention to small details to make sure records and tasks are accurate.",
        },
        {
            "id": "OR-3",
            "dimension": "Subject Preference",
            "prompt": "I enjoy and perform well in subjects that require neat documentation, bookkeeping, or strict procedures.",
        },
    ],
    "entrepreneurial": [
        {
            "id": "EN-1",
            "dimension": "Interest",
            "prompt": "I am interested in starting a business, selling products, or leading group projects.",
        },
        {
            "id": "EN-2",
            "dimension": "Ability",
            "prompt": "I can spot opportunities to improve a service, persuade others, or manage money wisely.",
        },
        {
            "id": "EN-3",
            "dimension": "Subject Preference",
            "prompt": "I enjoy and perform well in Entrepreneurship, Economics, or Business Management subjects.",
        },
    ],
}

# Backward-compatible alias
LAYER1_QUESTIONS = LAYER2_TRAIT_QUESTIONS

# Optional SHS-friendly prompt overrides for Layer 3 skills (falls back to skills.json hint)
LAYER3_SKILL_PROMPTS: dict[str, str] = {
    "sk_code": "I enjoy learning to write, test, and fix computer code.",
    "sk_imaging": "I'm interested in operating X-ray, ultrasound, or medical scan equipment.",
    "sk_techvoc": "I want to teach practical trade or technical skills to others.",
    "sk_communitymedia": "I'm interested in using media and campaigns to inform and help local communities.",
    "sk_casecare": "I like organizing welfare support and services for individuals or families in need.",
    "sk_securityops": "I'm interested in security systems, safety planning, and protecting facilities.",
}


def resolve_skill_prompt(skill: dict) -> str:
    """Return the SHS-refined prompt if defined, otherwise the catalog hint from skills.json."""
    skill_key = skill.get("key") or skill.get("id", "")
    return LAYER3_SKILL_PROMPTS.get(skill_key) or skill.get("hint", "")