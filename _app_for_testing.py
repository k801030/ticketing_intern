import concurrent.futures
import logging

from src.common.config import TixcraftConfig
from src.tixcraft import TixCraft


def main(config):
    app = TixCraft(config)
    app.setup_browser()
    app.set_cookie()
    app.close_consent()
    # app.login()

    app.execute()


def build_config() -> TixcraftConfig:
    facebook_account = 'partyhousetw@gmail.com'
    facebook_password = 'vi_movie'
    # ocr testing
    page = 'https://tixcraft.com/ticket/ticket/24_colde/17640/1/48'
    page = 'https://tixcraft.com/activity/detail/24_colde'
    # page = 'https://tixcraft.com/activity/detail/24_asmrmaxxx'
    return TixcraftConfig(
        target_page=page,
        facebook_account=facebook_account,
        facebook_password=facebook_password,
        num_of_interns=1,
    )


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    logging.info("Running against tixcraft...")
    config = build_config()

    app = TixCraft(config)
    app.setup_browser()
    app.close_consent()
    app.execute()
    # app.login()
    config.sid_cookie = app.fetch_sid()

    with concurrent.futures.ThreadPoolExecutor(max_workers=config.num_of_interns) as executor:
        futures = []
        for i in range(config.num_of_interns):
            future = executor.submit(main, config)
            futures.append(future)

        for future in concurrent.futures.as_completed(futures):
            future.result()
