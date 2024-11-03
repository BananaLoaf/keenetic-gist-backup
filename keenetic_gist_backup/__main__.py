import base64
from typing import Optional

import typer
from dotenv import load_dotenv
from github import Auth, Github, InputFileContent
from github.Gist import Gist
from loguru import logger

from keenetic_gist_backup.client import KeeneticClient

load_dotenv()


class Runner:
    keenetic_url_option = typer.Option(
        default="http://192.168.1.1/", envvar="KEENETIC_URL"
    )
    keenetic_username_option = typer.Option(..., envvar="KEENETIC_USERNAME")
    keenetic_password_option = typer.Option(..., envvar="KEENETIC_PASSWORD")
    github_token_option = typer.Option(..., envvar="GITHUB_TOKEN")
    gist_description_option = typer.Option(
        default="Keenetic Config Backup", envvar="GIST_DESCRIPTION"
    )

    def __init__(
        self,
        keenetic_url: str,
        keenetic_username: str,
        keenetic_password: str,
        github_token: str,
    ):
        self.keenetic_client = KeeneticClient(
            url=keenetic_url,
            username=keenetic_username,
            password=keenetic_password,
        )
        self.g = Github(auth=Auth.Token(github_token))

    @classmethod
    def healthcheck(
        cls,
        keenetic_url: str = keenetic_url_option,
        keenetic_username: str = keenetic_username_option,
        keenetic_password: str = keenetic_password_option,
        github_token: str = github_token_option,
    ):
        self = cls(
            keenetic_url=keenetic_url,
            keenetic_username=keenetic_username,
            keenetic_password=keenetic_password,
            github_token=github_token,
        )
        self.keenetic_client.auth()
        self.g.get_rate_limit()

    def get_gist(self, description: str) -> Optional[Gist]:
        for gist in self.g.get_user().get_gists():
            if gist.description == description:
                return gist

    @classmethod
    def backup(
        cls,
        keenetic_url: str = keenetic_url_option,
        keenetic_username: str = keenetic_username_option,
        keenetic_password: str = keenetic_password_option,
        github_token: str = github_token_option,
        gist_description: str = gist_description_option,
    ):
        self = cls(
            keenetic_url=keenetic_url,
            keenetic_username=keenetic_username,
            keenetic_password=keenetic_password,
            github_token=github_token,
        )
        self.keenetic_client.auth()

        config_filename, config_content = self.keenetic_client.startup_config()
        firmware_filename, firmware_content = self.keenetic_client.firmware()
        files = {
            config_filename: InputFileContent(config_content),
            firmware_filename: InputFileContent(
                base64.b64encode(firmware_content).decode()
            ),
        }

        gist = self.get_gist(description=gist_description)
        if gist is not None:
            gist.edit(description=gist_description, files=files)
            logger.success(f"Updated existing gist: {gist.html_url}")
        else:
            gist = self.g.get_user().create_gist(
                public=False,
                files=files,
                description=gist_description,
            )
            logger.success(f"Created new gist: {gist.html_url}")


def main():
    app = typer.Typer()
    app.command()(Runner.healthcheck)
    app.command()(Runner.backup)
    app()


if __name__ == "__main__":
    main()
