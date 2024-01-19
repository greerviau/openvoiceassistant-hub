import uvicorn
import click

from backend.src.api import create_app
from backend.ova import OpenVoiceAssistant

@click.command()
@click.option("--debug", is_flag=True)
def main(debug):
    ova = OpenVoiceAssistant()

    app = create_app(ova)
    uvicorn.run(app, host='0.0.0.0', port=5010 if debug else 7123)
    print("running")

if __name__ == '__main__':
    main()