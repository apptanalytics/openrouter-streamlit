import streamlit as st
import requests
import json
from shared import constants, utils


# Get available models from the API
def get_available_models():
    try:
        response = requests.get(constants.OPENROUTER_API_BASE + "/models")
        response.raise_for_status()
        models = json.loads(response.text)["data"]
        return [model["id"] for model in models]
    except requests.exceptions.RequestException as e:
        st.error(f"Error getting models from API: {e}")
        return []


# Handle the model selection process
def handle_model_selection(available_models, selected_model, default_model):
    # Determine the index of the selected model
    if selected_model and selected_model in available_models:
        selected_index = available_models.index(selected_model)
    else:
        selected_index = available_models.index(default_model)
    selected_model = st.selectbox(
        "Select a model", available_models, index=selected_index
    )
    return selected_model


def exchange_code_for_api_key(code: str):
    print(f"Exchanging code for API key: {code}")
    try:
        response = requests.post(
            constants.OPENROUTER_API_BASE + "/auth/keys",
            json={"code": code},
        )
        response.raise_for_status()
        st.query_params.clear()
        api_key = json.loads(response.text)["key"]
        st.session_state["api_key"] = api_key
        st.rerun()
    except requests.exceptions.RequestException as e:
        error_message = f"Error exchanging code for API key: {e}"
        if hasattr(e.response, 'text'):
            try:
                error_details = json.loads(e.response.text)
                error_message += f"\nDetails: {error_details}"
            except:
                error_message += f"\nResponse: {e.response.text}"
        st.error(error_message)
        print(error_message)


def sidebar(default_model):
    with st.sidebar:
        params = st.query_params
        # Get the code parameter and validate it
        code = params.get("code")
        if isinstance(code, list):
            code = code[0] if code else None
        if code and len(code) > 10:  # Basic validation that code looks reasonable
            exchange_code_for_api_key(code)
        # not storing sensitive api_key in query params
        api_key = st.session_state.get("api_key")
        selected_model = params.get("model", [None])[0] or st.session_state.get(
            "model", None
        )
        url = utils.url_to_hostname(utils.get_url())
        if not api_key:
            st.button(
                "Connect OpenRouter",
                on_click=utils.open_page,
                args=(f"{constants.OPENROUTER_BASE}/auth?callback_url={url}",),
            )
        available_models = get_available_models()
        selected_model = handle_model_selection(
            available_models, selected_model, default_model
        )
        st.session_state["model"] = selected_model
        st.query_params["model"] = selected_model

        if api_key:
            st.text("Connected to OpenRouter")
            if st.button("Log out"):
                del st.session_state["api_key"]
                st.rerun()
        st.markdown(
            "[View the source code](https://github.com/alexanderatallah/openrouter-streamlit)"
        )
        # st.markdown(
        #     "[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/alexanderatallah/openrouter-streamlit?quickstart=1)"
        # )

    return api_key, selected_model
