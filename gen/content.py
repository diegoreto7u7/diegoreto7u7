"""Todos los textos del perfil (ES/EN), misiones, habilidades y URLs."""

from dataclasses import dataclass

LANGS = ("es", "en")
PROJECT_TOTAL = 13

SKILLS: list[tuple[str, float]] = [
    ("PYTHON", 29.0), ("TYPESCRIPT", 28.9), ("C / C++", 20.7),
    ("GO", 5.7), ("PHP", 3.6), ("RUST", 2.8),
]
INVENTORY: list[str] = [
    "Python", "Go", "Rust", "Linux", "Docker", "Kubernetes",
    "PostgreSQL", "React", "CUDA", "DeepStream",
]


@dataclass(frozen=True)
class Quest:
    slug: str
    title: dict[str, str]
    summary: dict[str, str]
    stack: str
    status: dict[str, str]
    starred: bool
    icon: str
    in_progress: bool = False


QUESTS: list[Quest] = [
    Quest(
        "conteobk",
        {"es": "ConteoBK", "en": "ConteoBK"},
        {"es": "Control de aforo con visión artificial y vídeo en tiempo real.",
         "en": "Occupancy control with computer vision and real-time video."},
        "Python · DeepStream · YOLO · Kubernetes",
        {"es": "Sistema desplegado", "en": "Deployed system"},
        True, "camera",
    ),
    Quest(
        "licitaciones",
        {"es": "Licitaciones", "en": "Public Tenders"},
        {"es": "Encontrar oportunidades públicas y analizar sus pliegos.",
         "en": "Find public procurement opportunities and analyze tender specs."},
        "Laravel · React · PostgreSQL · IA",
        {"es": "Proyecto desarrollado", "en": "Completed project"},
        True, "document",
    ),
    Quest(
        "nectum",
        {"es": "Nectum", "en": "Nectum"},
        {"es": "Un ERP modular en Rust para ventas, stock y contabilidad.",
         "en": "A modular Rust ERP for sales, inventory and accounting."},
        "Rust · Axum · Tokio · SQLx",
        {"es": "En desarrollo", "en": "In development"},
        False, "crab", True,
    ),
    Quest(
        "smart-city-platform",
        {"es": "Garu-City", "en": "Garu-City"},
        {"es": "Una plataforma para conectar los servicios de una ciudad.",
         "en": "A platform connecting the services of a smart city."},
        "Go · PostGIS · NATS · MapLibre",
        {"es": "En desarrollo", "en": "In development"},
        False, "city", True,
    ),
]

# En la stack EN, «IA» se escribe «AI».
_STACK_EN = {"licitaciones": "Laravel · React · PostgreSQL · AI"}

_SITE = "https://diegoret.pages.dev"
URLS: dict[str, dict[str, str]] = {
    "es": {
        "portfolio": f"{_SITE}/",
        "cv": f"{_SITE}/cv-diego-orue.pdf",
        "linkedin": "https://www.linkedin.com/in/diegoret",
        "email": "mailto:orueret@gmail.com",
        "lang": "https://github.com/diegoreto7u7/diegoreto7u7/blob/main/README.en.md",
        **{f"quest.{q.slug}": f"{_SITE}/proyectos/{q.slug}/" for q in QUESTS},
    },
    "en": {
        "portfolio": f"{_SITE}/en/",
        "cv": f"{_SITE}/cv-diego-orue.pdf",
        "linkedin": "https://www.linkedin.com/in/diegoret",
        "email": "mailto:orueret@gmail.com",
        "lang": "https://github.com/diegoreto7u7",
        **{f"quest.{q.slug}": f"{_SITE}/en/projects/{q.slug}/" for q in QUESTS},
    },
}

COPY: dict[str, dict[str, str]] = {
    "es": {
        "intro": "**Diego Orue** · Desarrollador de software en Bilbao · Backend, visión artificial y datos",
        "hero.role": "Desarrollador de software · Bilbao",
        "hero.t1": "$ whoami",
        "hero.t2": "Diego · backend, visión y datos",
        "hero.t3": "$ cat lenguajes.txt",
        "hero.t4": "Python TS C/C++ Go Rust PHP Java",
        "hero.t5": "$ ./conteobk --cam 03",
        "hero.t6": "> modelo YOLO cargado... OK",
        "hero.t7": "> pipeline en marcha",
        "hero.person": "persona",
        "hero.count": "AFORO",
        "hero.exit": "SALIDA",
        "hero.nosignal": "SIN SEÑAL",
        "btn.portfolio": "PORTFOLIO",
        "btn.linkedin": "LINKEDIN",
        "btn.email": "CORREO",
        "btn.cv": "CV",
        "btn.lang": "ENGLISH",
        "sheet.title": "FICHA DE PERSONAJE",
        "sheet.class": "CLASE",
        "sheet.guild": "GREMIO",
        "sheet.base": "BASE",
        "sheet.origin": "ORIGEN",
        "sheet.langs": "IDIOMAS",
        "sheet.skills": "HABILIDADES",
        "sheet.class_v": "Backend · Visión artificial · Datos",
        "sheet.guild_v": "Radimer Seguridad · desde 2025",
        "sheet.base_v": "Bilbao",
        "sheet.origin_v": "Pasé por los videojuegos con Unity (300 h) antes de acabar montando pipelines de visión.",
        "sheet.exp": "EXP {total} contribuciones · {active}/{window} días activos",
        "ach.title": "LOGROS DESBLOQUEADOS",
        "ach.toast": "¡Logro desbloqueado!",
        "ach.best_day": "{n} contribuciones en un solo día",
        "ach.langs": "36 lenguajes en mis repos",
        "ach.gpu": "Vídeo en tiempo real sobre GPU: DeepStream + Triton",
        "ach.rag": "RAG sobre +5 millones de registros públicos",
        "ach.rust": "ERP modular en Rust",
        "ach.go": "Plataforma smart city en Go",
        "ach.streak_current": "Racha actual: {n} días seguidos",
        "ach.streak_longest": "Racha récord: {n} días seguidos",
        "inv.title": "INVENTARIO",
        "quests.title": "MISIONES",
        "quests.more": "+{n} misiones más en diegoret.pages.dev",
        "hs.title": "HIGH SCORE",
        "hs.score": "1UP {total}",
        "hs.best": "RÉCORD {n}/DÍA",
        "footer.start": "PULSA START PARA HABLAR CONMIGO",
        "alt.lang": "Botón ENGLISH: cambia a la versión del perfil en inglés.",
        "alt.hero": (
            "Diego Orue, desarrollador de software en Bilbao. Una terminal pixel art escribe: "
            "$ whoami, Diego · backend, visión y datos, $ cat lenguajes.txt, "
            "Python TS C/C++ Go Rust PHP Java, $ ./conteobk --cam 03, "
            "> modelo YOLO cargado... OK, > pipeline en marcha. "
            "Junto a la terminal, una cámara pixel art detecta personas y marca el AFORO."
        ),
        "alt.sheet": (
            "Ficha de personaje. Clase: Backend, visión artificial y datos. "
            "Gremio: Radimer Seguridad, desde 2025. Base: Bilbao. "
            "Origen: pasé por los videojuegos con Unity (300 h) antes de acabar montando pipelines de visión. "
            "Idiomas: español nativo, inglés B2, euskera B2. Habilidades: Python 29,0 %, TypeScript 28,9 %, C / C++ 20,7 %, Go 5,7 %, PHP 3,6 %, Rust 2,8 %. "
            "EXP {total} contribuciones, {active} de {window} días activos."
        ),
        "alt.achievements": (
            "Logros desbloqueados: {best} contribuciones en un solo día; 36 lenguajes en mis repos; "
            "vídeo en tiempo real sobre GPU con DeepStream y Triton; RAG sobre más de 5 millones de registros públicos; "
            "ERP modular en Rust; plataforma smart city en Go; {streak}."
        ),
        "alt.inventory": (
            "Inventario de herramientas: Python, Go, Rust, Linux, Docker, Kubernetes, "
            "PostgreSQL, React, CUDA y DeepStream."
        ),
        "alt.highscore": (
            "High score: 1UP {total} contribuciones y récord de {best} contribuciones en un día."
        ),
        "alt.bilbao": (
            "Bilbao de noche en pixel art, con estrellas que titilan, ventanas encendidas y reflejos en el agua: "
            "el Guggenheim, el Puppy, el arco rojo del puente de La Salve, la torre Iberdrola, "
            "el puente Zubizuri, los montes de Artxanda y la ría."
        ),
    },
    "en": {
        "intro": "**Diego Orue** · Software developer in Bilbao, Spain · Backend, computer vision & data",
        "hero.role": "Software developer · Bilbao",
        "hero.t1": "$ whoami",
        "hero.t2": "Diego · backend, vision & data",
        "hero.t3": "$ cat languages.txt",
        "hero.t4": "Python TS C/C++ Go Rust PHP Java",
        "hero.t5": "$ ./conteobk --cam 03",
        "hero.t6": "> YOLO model loaded... OK",
        "hero.t7": "> pipeline running",
        "hero.person": "person",
        "hero.count": "PEOPLE",
        "hero.exit": "EXIT",
        "hero.nosignal": "NO SIGNAL",
        "btn.portfolio": "PORTFOLIO",
        "btn.linkedin": "LINKEDIN",
        "btn.email": "EMAIL",
        "btn.cv": "CV",
        "btn.lang": "ESPAÑOL",
        "sheet.title": "CHARACTER SHEET",
        "sheet.class": "CLASS",
        "sheet.guild": "GUILD",
        "sheet.base": "BASE",
        "sheet.origin": "ORIGIN",
        "sheet.langs": "LANGUAGES",
        "sheet.skills": "SKILLS",
        "sheet.class_v": "Backend · Computer vision · Data",
        "sheet.guild_v": "Radimer Seguridad · since 2025",
        "sheet.base_v": "Bilbao, Spain",
        "sheet.origin_v": "I went through game dev with Unity (300 h) before ending up building vision pipelines.",
        "sheet.exp": "EXP {total} contributions · {active}/{window} active days",
        "ach.title": "ACHIEVEMENTS UNLOCKED",
        "ach.toast": "Achievement unlocked!",
        "ach.best_day": "{n} contributions in a single day",
        "ach.langs": "36 languages across my repos",
        "ach.gpu": "Real-time GPU video: DeepStream + Triton",
        "ach.rag": "RAG over 5M+ public records",
        "ach.rust": "Modular ERP in Rust",
        "ach.go": "Smart city platform in Go",
        "ach.streak_current": "Current streak: {n} days in a row",
        "ach.streak_longest": "Longest streak: {n} days in a row",
        "inv.title": "INVENTORY",
        "quests.title": "QUESTS",
        "quests.more": "+{n} more quests at diegoret.pages.dev",
        "hs.title": "HIGH SCORE",
        "hs.score": "1UP {total}",
        "hs.best": "BEST {n}/DAY",
        "footer.start": "PRESS START TO GET IN TOUCH",
        "alt.lang": "ESPAÑOL button: switches to the Spanish version of the profile.",
        "alt.hero": (
            "Diego Orue, software developer in Bilbao. A pixel art terminal types: "
            "$ whoami, Diego · backend, vision & data, $ cat languages.txt, "
            "Python TS C/C++ Go Rust PHP Java, $ ./conteobk --cam 03, "
            "> YOLO model loaded... OK, > pipeline running. "
            "Next to the terminal, a pixel art camera detects people and counts them as PEOPLE."
        ),
        "alt.sheet": (
            "Character sheet. Class: Backend, computer vision and data. "
            "Guild: Radimer Seguridad, since 2025. Base: Bilbao, Spain. "
            "Origin: I went through game dev with Unity (300 h) before ending up building vision pipelines. "
            "Languages: Spanish (native), English (B2), Basque (B2). Skills: Python 29.0%, TypeScript 28.9%, C / C++ 20.7%, Go 5.7%, PHP 3.6%, Rust 2.8%. "
            "EXP {total} contributions, {active} of {window} days active."
        ),
        "alt.achievements": (
            "Achievements unlocked: {best} contributions in a single day; 36 languages across my repos; "
            "real-time GPU video with DeepStream and Triton; RAG over more than 5 million public records; "
            "modular ERP in Rust; smart city platform in Go; {streak}."
        ),
        "alt.inventory": (
            "Tool inventory: Python, Go, Rust, Linux, Docker, Kubernetes, "
            "PostgreSQL, React, CUDA and DeepStream."
        ),
        "alt.highscore": (
            "High score: 1UP {total} contributions and a best of {best} contributions in one day."
        ),
        "alt.bilbao": (
            "Bilbao at night in pixel art, with twinkling stars, lit windows and water reflections: "
            "the Guggenheim, the Puppy sculpture, the red arch of La Salve bridge, the Iberdrola tower, "
            "the Zubizuri bridge, the Artxanda hills and the estuary (ria)."
        ),
    },
}


def quest_stack(q: Quest, lang: str) -> str:
    return _STACK_EN.get(q.slug, q.stack) if lang == "en" else q.stack


def fmt_int(n: int, lang: str) -> str:
    s = f"{n:,}"
    return s.replace(",", ".") if lang == "es" else s
