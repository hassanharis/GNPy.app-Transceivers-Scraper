from playwright.sync_api import sync_playwright
import pandas as pd
import time

URL = "https://gnpy.app/"


def extract_value(page, input_id):
    """Extract value from input field using JavaScript to get DOM value property"""
    try:
        # Use evaluate to get the actual DOM value property (not HTML attribute)
        value = page.evaluate(f"document.querySelector('#{input_id}')?.value || ''")
        return value if value else None
    except:
        pass
    return None


def open_dropdown(page, selector):
    control = page.locator(selector + " .Select-control")
    control.click()
    page.wait_for_timeout(500)
    
    # Wait for options to render (ReactVirtualized needs time)
    try:
        page.wait_for_selector(".ReactVirtualized__Grid__innerScrollContainer > div", timeout=5000)
    except:
        pass  # Options may already be visible


def get_options(page):
    # Try ReactVirtualized options first (most common)
    options = page.locator(".ReactVirtualized__Grid__innerScrollContainer > div")
    count = options.count()
    
    # Fallback to standard Select-option
    if count == 0:
        options = page.locator(".Select-menu-outer .Select-option")
        count = options.count()
    
    return [options.nth(i).inner_text().strip() for i in range(count)]


def close_dropdown(page):
    """Close any open dropdown"""
    page.keyboard.press("Escape")
    page.wait_for_timeout(200)
    page.locator("body").click(position={"x": 10, "y": 10})
    page.wait_for_timeout(300)


def wait_for_mode_enabled(page):
    """Wait until mode dropdown is no longer disabled"""
    page.wait_for_function("""
        () => {
            const el = document.querySelector('#trx-mode .Select');
            return el && !el.classList.contains('is-disabled');
        }
    """)

def get_options_scrolled(page):
    """Get all options from a ReactVirtualized dropdown by scrolling through it"""
    all_options = set()
    
    # Get the scrollable container
    scroll_container = page.locator(".ReactVirtualized__Grid")
    
    if scroll_container.count() == 0:
        # Fallback to standard Select-option
        options = page.locator(".Select-menu-outer .Select-option")
        return [options.nth(i).inner_text().strip() for i in range(options.count())]
    
    # Scroll to top first
    scroll_container.evaluate("el => el.scrollTop = 0")
    page.wait_for_timeout(200)
    
    last_count = 0
    max_scrolls = 50  # Safety limit
    
    for _ in range(max_scrolls):
        # Get currently visible options
        visible_options = page.locator(".ReactVirtualized__Grid__innerScrollContainer > div")
        for i in range(visible_options.count()):
            text = visible_options.nth(i).inner_text().strip()
            if text:
                all_options.add(text)
        
        # Check if we've found new options
        if len(all_options) == last_count:
            break  # No new options, we've seen them all
        last_count = len(all_options)
        
        # Scroll down
        scroll_container.evaluate("el => el.scrollTop += 150")
        page.wait_for_timeout(100)
    
    return list(all_options)

def run():
    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(URL)

        page.wait_for_timeout(3000)

        # --- Get transceivers ---
        open_dropdown(page, "#trx-type")
        page.wait_for_timeout(300)
        trx_list = get_options_scrolled(page)
        close_dropdown(page)

        print(f"Found {len(trx_list)} transceivers")

        for trx in trx_list:
            print(f"\n=== TRX: {trx} ===")
            
            # Open transceiver dropdown and select
            open_dropdown(page, "#trx-type")
            page.wait_for_timeout(300)
            options = page.locator(".ReactVirtualized__Grid__innerScrollContainer > div")

            #get_options(page)  # Ensure options are loaded before clicking
            for i in range(options.count()):
                if options.nth(i).inner_text().strip() == trx:
                    options.nth(i).click()
                    break
            page.wait_for_timeout(500)
            
            # Wait for mode dropdown to be enabled
            wait_for_mode_enabled(page)
            
            # --- Get modes ---
            open_dropdown(page, "#trx-mode")
            page.wait_for_timeout(500)
            mode_list = get_options(page)
            # close_dropdown(page)
            
            print(f"  Found {len(mode_list)} modes")


            for mode in mode_list:
                print(f"    {mode}...", end=" ", flush=True)
                
                # Open mode dropdown and select directly
                # page.locator("#trx-mode .Select-control").click(force=True)
                open_dropdown(page, "#trx-mode")
                page.wait_for_timeout(500)
                
                # Find and click the option
                mode_options = page.locator(".ReactVirtualized__Grid__innerScrollContainer > div")
                for i in range(mode_options.count()):
                    if mode_options.nth(i).inner_text().strip() == mode:
                        mode_options.nth(i).click()
                        break
                page.wait_for_timeout(500)

                # Wait for values to populate
                page.wait_for_timeout(300)

                # Debug: check what value we're getting
                debug_val = page.evaluate("document.querySelector('#baudrate')?.value || 'EMPTY'")
                print(f"\nDEBUG: baudrate value = '{debug_val}'")

                margin = extract_value(page, "system-margin")
                baud = extract_value(page, "baudrate")
                rolloff = extract_value(page, "roll-off")
                tx_osnr = extract_value(page, "tx-osnr")
                min_osnr = extract_value(page, "required-osnr")
                
                print(f"  Extracted: margin={margin}, baud={baud}, rolloff={rolloff}")

                results.append({
                    "transceiver": trx,
                    "mode": mode,
                    "Margin_dB": margin,
                    "Baudrate_Gbaud": baud,
                    "Roll_off": rolloff,
                    "Tx_OSNR_dB": tx_osnr,
                    "Min_OSNR_dB": min_osnr
                })
                
                print(f"Margin: {margin}")

        browser.close()

    df = pd.DataFrame(results)
    df.to_csv("gnpy_results.csv", index=False)
    print(f"\nSaved {len(results)} results to gnpy_results.csv")


if __name__ == "__main__":
    run()