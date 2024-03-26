## About
Sophi is a multi-function agent. With the ability to access other minor agents for better quality.

## Installation
Recommended to install llama-cpp-python with gpu
- Follow instructions here: [`llama-cpp-python`](https://github.com/abetlen/llama-cpp-python)

Install requirements:
```bash
git clone https://github.com/DrakeVoong/Sophi.git

cd Sophi

pip install -r requirements.txt
```

## Configuration
#### Hugging Face Hub User Access Token
To download and check for models a Hugging Face user access token is required.

1. Create `.env` file in `Sophi/` directory.
2. Set `HUGGINGFACE_HUB=[your_hf_hub_key]`

Never share your api keys to the public.

## RoadMap / Planned Ideas

- [ ] Editor for helper roles
- [ ] Editor for model prompting
- [ ] Default settings on web-UI launch

## License
This project is licensed under the terms of the [`MIT License`](https://opensource.org/license/mit).