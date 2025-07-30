from geocleaner.core import clean_location, clean_locations

def test_clean_location():
    assert clean_location(" 123 main st. ") == "123 Main Street"
    assert clean_location("456  Elm Rd") == "456 Elm Road"

def test_clean_locations():
    data = ["1 oak ave", "55 cedar blvd "]
    cleaned = clean_locations(data)
    assert cleaned == ["1 Oak Avenue", "55 Cedar Boulevard"]
