from robocorp.tasks import task
from robocorp import browser

from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive

@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    browser.configure(
        slowmo=50,
    )
    open_robot_order_website()
    tab_selection()
    close_annoying_modal()
    download_csv_file()
    orders = get_orders()
    for order in orders:
        fill_the_form(order)
        see_preview()
        send_order(order)
    archive_receipts()

def open_robot_order_website():
    """Navigates to the given URL"""
    browser.goto("https://robotsparebinindustries.com/")

def tab_selection():
    """Tab selection to otder your robot"""
    page = browser.page()
    page.click("text=Order your robot!")
    

def close_annoying_modal():
    """Close modal"""
    page = browser.page()
    page.click("text=OK")

def download_csv_file():
    """Downloads csv file from the given URL"""
    http = HTTP()
    http.download(url="https://robotsparebinindustries.com/orders.csv", overwrite=True)

def get_orders():
    library = Tables()
    return library.read_table_from_csv("orders.csv")

def fill_the_form(order):
    page = browser.page()
    
    page.select_option("#head", str(order['Head']))
    page.click("#id-body-" + order['Body'])
    page.fill("input[placeholder='Enter the part number for the legs']", order["Legs"])
    page.fill("#address", str(order["Address"]))

def see_preview():
    page = browser.page()
    page.click("#preview")

def send_order(order):
    page = browser.page()

    while True:
        page.click("#order")
        order_another = page.query_selector("#order-another")
        if order_another:
            order_number = order['Order number']
            pdf_file = store_receipt_as_pdf(order_number)
            screenshot = screenshot_robot(order_number)
            embed_screenshot_to_receipt(screenshot, pdf_file)
            order_another_robot()
            close_annoying_modal()
            break

    if page.is_visible("text=External Server Error"):
      send_order()
        
def order_another_robot():
    page = browser.page()
    page.click("text=Order another robot")

def store_receipt_as_pdf(order_number):
    """This stores the robot order receipt as pdf"""
    page = browser.page()
    order_receipt_html = page.locator("#receipt").inner_html()
    pdf = PDF()
    pdf_path = "output/receipts/{0}.pdf".format(order_number)
    pdf.html_to_pdf(order_receipt_html, pdf_path)
    return pdf_path

def screenshot_robot(order_number):
    """Takes screenshot of the ordered bot image"""
    page = browser.page()
    screenshot_path = "output/screenshots/{0}.png".format(order_number)
    page.locator("#robot-preview-image").screenshot(path=screenshot_path)
    return screenshot_path

def embed_screenshot_to_receipt(screenshot_path, pdf_path):
    """Embeds the screenshot to the bot receipt"""
    pdf = PDF()
    pdf.add_watermark_image_to_pdf(image_path=screenshot_path, 
                                   source_path=pdf_path, 
                                   output_path=pdf_path)
    
def archive_receipts():
    lib = Archive()
    lib.archive_folder_with_zip("./output/receipts", "./output/receipts.zip")