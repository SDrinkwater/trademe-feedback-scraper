import sys
import re
import argparse
import requests
from lxml import html

parser = argparse.ArgumentParser(
    description="Scrape feedback details from TradeMe members"
)
parser.add_argument(
    "-m",
    "--member",
    action="store",
    dest="member_id",
    help="member id to scrape feedback from, e.g., 9999999",
    required=True,
)
parser.add_argument(
    "-p",
    "--page",
    action="store",
    dest="input_page",
    help="feedback page number to scrape, e.g., 1",
    default=1,
)
parser.add_argument(
    "-l",
    "--limit",
    action="store",
    dest="limit",
    help="limit the number of scraped feedback entries, e.g., 50",
    default=50,
)
parser.add_argument(
    "-o",
    "--output",
    action="store",
    dest="output_filename",
    help="output filename, e.g., samuels-feedback",
    default=None,
)
args = vars(parser.parse_args())


def clean_ids(ids):
    cleaned = []
    for id in ids:
        cleaned.append(id.replace("(#", "").replace(")", ""))
    return cleaned


def fetch_auction_ids(member_id, target_page=1):
    page = requests.get(
        "https://www.trademe.co.nz/Members/Feedback.aspx?type=s&member="
        + str(member_id)
        + "&page="
        + str(target_page)
    )
    tree = html.fromstring(page.content)
    member = tree.xpath("//div[@id='membersection']//span/a[@id='MemberLink']/text()")
    raw_ids = tree.xpath("//span[contains(., '(#')]/text()")
    auction_ids = clean_ids(raw_ids)
    return auction_ids, member


def fetch_auction(auction_id):
    url = "https://www.trademe.co.nz/Archive/Browse/Listing.aspx?id=" + auction_id
    page = requests.get(url)
    tree = html.fromstring(page.content)
    title, date = tree.xpath(
        "//div[@id='ListingTitleBox_TitleText']/h1/text() | //span[@id='ClosingTime_ClosingTime']/text()"
    )
    return [url, title, date.replace(",", "")]


def draw_progress_bar(percent, message="test", barLen=30):
    sys.stdout.write("\r")
    progress = ""
    for i in range(barLen):
        if i < int(barLen * percent):
            progress += "="
        else:
            progress += " "
    sys.stdout.write("[ %s ] %.2f%% - " % (progress, percent * 100) + message)
    sys.stdout.flush()


def write_csv(output, data):
    separator = "|"
    with open(output + ".csv", "w") as csv_file:
        csv_file.write("sep=" + separator + "\n")
        for line in data:
            csv_file.write(separator.join(line) + "\n")


def run():
    if args["member_id"]:
        auction_ids, member = fetch_auction_ids(args["member_id"], args["input_page"])
        auction_info = [["Url", "Title", "Date"]]
        id_count = len(auction_ids)
        for idx, id in enumerate(auction_ids[: args["limit"]]):
            draw_progress_bar(idx / (id_count - 1), "fetching auction " + id)
            auction_info.append(fetch_auction(id))

        output_target = (
            args["output_filename"]
            if args["output_filename"] is not None
            else member[0] + "-" + str(args["member_id"])
        )
        write_csv(output_target, auction_info)
        print("\nFeedback written to", output_target + ".csv")
    else:
        parser.print_help()
        sys.exit(0)


run()
