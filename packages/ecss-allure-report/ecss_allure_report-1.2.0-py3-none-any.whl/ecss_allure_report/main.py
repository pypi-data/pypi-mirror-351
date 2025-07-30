import os
#from pathlib import Path

from diagram import create_diagram
from dotenv import load_dotenv
from summary import generate_summary

from ecss_chat_client import Client


load_dotenv()


def send_report():
    #current_dir = Path(__file__).parent
    cwd = os.getcwd()
    output_path = cwd / str(os.getenv('REPORT_DIAGRAM_NAME'))
    print(output_path)
    create_diagram(output_path)
    client = Client(
        server=os.getenv('REPORT_ELPH_SERVER'),
        username=os.getenv('REPORT_ELPH_USER'),
        password=os.getenv('REPORT_ELPH_PASSWORD')
    )

    version = client.different.version()
    version = version.json()

    summary = generate_summary(
        project_name=os.getenv('REPORT_PROJECT_NAME'),
        version=version.get('version'),
    )

    client.rooms.upload_file(
        os.getenv('REPORT_ELPH_ROOM_ID'),
        summary,
        output_path
    )


if __name__ == "__main__":
    send_report()
