import base64
import os
from pathlib import Path

import requests
import streamlit as st


st.set_page_config(page_title="PixelForge AI", page_icon=":art:", layout="wide")


INVOKE_URL = "https://ai.api.nvidia.com/v1/genai/stabilityai/stable-diffusion-3-medium"

STYLE_PRESETS = {
    "None": "",
    "Cinematic": "cinematic composition, dramatic lighting, film still, volumetric light, highly detailed",
    "Anime": "anime illustration, clean line art, vibrant colors, expressive characters, studio quality",
    "Realistic": "photorealistic, natural lighting, sharp focus, realistic textures, high dynamic range",
    "3D Render": "3D octane render, global illumination, depth of field, physically based materials",
    "Fantasy Art": "epic fantasy concept art, magical atmosphere, intricate details, painterly masterpiece",
}


def get_api_key():
    # Avoid touching st.secrets when no secrets file exists.
    user_secrets_path = Path.home() / ".streamlit" / "secrets.toml"
    project_secrets_path = Path.cwd() / ".streamlit" / "secrets.toml"

    if user_secrets_path.exists() or project_secrets_path.exists():
        try:
            secret_key = st.secrets.get("NVIDIA_API_KEY")
            if secret_key:
                return secret_key
        except Exception:
            pass

    env_key = os.getenv("NVIDIA_API_KEY")
    if env_key:
        return env_key

    try:
        from NVIDIA_API_KEY import NVIDIA_API_KEY as local_api_key

        if local_api_key:
            return local_api_key
    except Exception:
        pass

    return None


API_KEY = get_api_key()


def _extract_images_from_response(response_body):
    images = []

    artifacts = response_body.get("artifacts", [])
    for artifact in artifacts:
        b64_data = artifact.get("base64")
        if b64_data:
            images.append(base64.b64decode(b64_data))

    if not images:
        image_key = response_body.get("image")
        if isinstance(image_key, str):
            images.append(base64.b64decode(image_key))

    if not images:
        data_key = response_body.get("data")
        if isinstance(data_key, list):
            for item in data_key:
                if isinstance(item, str):
                    images.append(base64.b64decode(item))

    return images


def generate_images(prompt, num_images):
    if not API_KEY:
        raise RuntimeError(
            "NVIDIA API key not found. Set NVIDIA_API_KEY in Streamlit secrets or environment."
        )

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Accept": "application/json",
    }

    payload = {"prompt": prompt}

    images = []
    for _ in range(num_images):
        response = requests.post(INVOKE_URL, headers=headers, json=payload, timeout=120)
        response.raise_for_status()
        response_body = response.json()
        images.extend(_extract_images_from_response(response_body))

    if not images:
        raise RuntimeError("No image data found in API response.")

    return images[:num_images]


st.markdown(
    """
    <style>
    :root {
        --bg-1: #081425;
        --bg-2: #13233f;
        --card: rgba(12, 26, 47, 0.68);
        --ink: #f3f7ff;
        --muted: #d7e5ff;
        --accent: #22d3ee;
        --accent-2: #f97316;
    }

    p, label, .stMarkdown, .stCaption {
        color: var(--ink);
    }

    [data-testid="stCaptionContainer"] p {
        color: var(--muted) !important;
        font-weight: 500;
    }

    [data-testid="stTextArea"] label p,
    [data-testid="stNumberInput"] label p,
    [data-testid="stRadio"] label p {
        color: #eaf2ff !important;
        font-weight: 700;
        letter-spacing: 0.01em;
    }

    .stApp {
        background:
            radial-gradient(1000px 540px at -8% -14%, rgba(34, 211, 238, 0.35) 0%, transparent 62%),
            radial-gradient(940px 520px at 108% -6%, rgba(249, 115, 22, 0.32) 0%, transparent 66%),
            radial-gradient(700px 480px at 50% 120%, rgba(71, 85, 255, 0.25) 0%, transparent 72%),
            linear-gradient(135deg, var(--bg-1), var(--bg-2));
    }

    .hero {
        padding: 1.4rem 1.4rem 1rem 1.4rem;
        border-radius: 18px;
        border: 1px solid rgba(162, 190, 255, 0.22);
        background: var(--card);
        backdrop-filter: blur(8px);
        box-shadow: 0 18px 36px rgba(3, 8, 18, 0.45);
        margin-bottom: 1rem;
    }

    .hero h1 {
        margin: 0;
        font-size: clamp(1.9rem, 4vw, 3rem);
        letter-spacing: 0.02em;
        color: var(--ink);
        font-weight: 800;
    }

    .hero p {
        margin: 0.35rem 0 0 0;
        color: var(--muted);
        font-size: 1rem;
    }

    .pill {
        display: inline-block;
        margin-top: 0.8rem;
        padding: 0.3rem 0.7rem;
        border-radius: 999px;
        border: 1px solid rgba(34, 211, 238, 0.45);
        background: rgba(34, 211, 238, 0.14);
        color: #b6f5ff;
        font-size: 0.84rem;
        font-weight: 600;
    }

    .stButton > button {
        border-radius: 12px;
        border: 0;
        background: linear-gradient(135deg, var(--accent), var(--accent-2));
        color: #ffffff;
        font-weight: 700;
        padding: 0.65rem 1rem;
        box-shadow: 0 12px 26px rgba(34, 211, 238, 0.35);
        transition: transform 0.15s ease;
    }

    .stButton > button:hover {
        transform: translateY(-1px);
    }

    [data-testid="stTextArea"] textarea {
        background: rgba(8, 18, 34, 0.9) !important;
        color: #f5f9ff !important;
        border: 1px solid rgba(34, 211, 238, 0.55) !important;
        border-radius: 12px !important;
    }

    [data-testid="stTextArea"] textarea::placeholder {
        color: #9db4d6 !important;
    }

    [data-testid="stTextArea"] textarea:focus {
        border-color: rgba(249, 115, 22, 0.85) !important;
        box-shadow: 0 0 0 1px rgba(249, 115, 22, 0.45), 0 0 0 4px rgba(249, 115, 22, 0.12) !important;
    }

    [data-testid="stNumberInput"] input {
        background: rgba(8, 18, 34, 0.9) !important;
        color: #f5f9ff !important;
        border: 1px solid rgba(34, 211, 238, 0.55) !important;
        border-radius: 12px !important;
        font-weight: 700;
    }

    [data-testid="stNumberInput"] input:focus {
        border-color: rgba(34, 211, 238, 0.95) !important;
        box-shadow: 0 0 0 1px rgba(34, 211, 238, 0.45), 0 0 0 4px rgba(34, 211, 238, 0.14) !important;
    }

    div[role="radiogroup"] {
        gap: 0.5rem;
        flex-wrap: wrap;
    }

    div[role="radiogroup"] label {
        border: 1px solid rgba(124, 158, 235, 0.5);
        border-radius: 999px;
        padding: 0.35rem 0.8rem;
        background: rgba(9, 23, 42, 0.74);
        transition: all 0.18s ease;
    }

    div[role="radiogroup"] label:hover {
        border-color: rgba(34, 211, 238, 0.8);
        box-shadow: 0 6px 14px rgba(5, 10, 25, 0.45);
    }

    div[role="radiogroup"] label:has(input:checked) {
        background: linear-gradient(135deg, rgba(34, 211, 238, 0.28), rgba(249, 115, 22, 0.26));
        border-color: rgba(34, 211, 238, 0.95);
        box-shadow: 0 10px 20px rgba(34, 211, 238, 0.3);
    }

    div[role="radiogroup"] label p {
        font-weight: 600;
        color: #e9f1ff;
        margin: 0;
    }

    @media (max-width: 768px) {
        .hero {
            padding: 1rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
      <h1>PixelForge AI</h1>
      <p>Turn one line of imagination into bold, high-detail artwork.</p>
      <span class="pill">Model: Stable Diffusion 3 Medium</span>
    </div>
    """,
    unsafe_allow_html=True,
)

left, right = st.columns([2.2, 1])
with left:
    style_name = st.radio(
        "Style Preset",
        options=list(STYLE_PRESETS.keys()),
        horizontal=True,
        index=1,
    )
    st.caption("Tap a style chip to instantly boost your prompt tone.")
    prompt = st.text_area(
        "Creative Prompt",
        placeholder="Example: A retro-futuristic city at sunrise, cinematic lighting, ultra detailed",
        height=140,
    )
with right:
    num_images = st.number_input("Number of Images", min_value=1, max_value=5, value=1)
    st.caption("More images means slower generation.")

if st.button("Generate Image"):
    if not prompt.strip():
        st.warning("Please enter a prompt.")
    else:
        try:
            style_suffix = STYLE_PRESETS.get(style_name, "")
            final_prompt = prompt.strip() if not style_suffix else f"{prompt.strip()}, {style_suffix}"

            with st.spinner("Generating image..."):
                images = generate_images(prompt=final_prompt, num_images=int(num_images))

            st.markdown("### Results")
            st.caption(f"Applied style: {style_name}")
            gallery_cols = st.columns(min(len(images), 3))
            for idx, image_bytes in enumerate(images, start=1):
                with gallery_cols[(idx - 1) % len(gallery_cols)]:
                    st.image(image_bytes, caption=f"Generated Image {idx}")
        except requests.HTTPError as exc:
            error_text = exc.response.text if exc.response is not None else str(exc)
            st.error(f"API request failed: {error_text}")
        except Exception as exc:
            st.error(f"Image generation failed: {exc}")