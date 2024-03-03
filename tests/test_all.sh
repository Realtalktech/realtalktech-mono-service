#!/bin/bash

# Function to output separators for readability
print_section() {
    echo "================================================================"
    echo "$1"
    echo "================================================================"
}

# Connect to the RDS instance
print_section "Testing login endpoints"
if pytest tests/test_login_endpoints.py; then
    echo "Login test success."
else
    echo "Login endpoint failure."
    exit 1  # Exit the script if there's a failure
fi

print_section "Testing post endpoints"
if pytest tests/test_login_endpoints.py; then
    echo "Post test success."
else
    echo "Post endpoint failure."
    exit 1  # Exit the script if there's a failure
fi

print_section "Testing user endpoints"
if pytest tests/test_user_endpoints.py; then
    echo "User test success."
else
    echo "User endpoint failure."
    exit 1  # Exit the script if there's a failure
fi

print_section "Testing vendor endpoints"
if pytest tests/test_vendor_endpoints.py; then
    echo "Vendor test success."
else
    echo "Vendor endpoint failure."
    exit 1  # Exit the script if there's a failure
fi

print_section "Testing comment endpoints"
if pytest tests/test_comment_endpoints.py; then
    echo "Comment test success."
else
    echo "Comment endpoint failure."
    exit 1  # Exit the script if there's a failure
fi


print_section "Testing feed endpoints"
if pytest tests/test_feed_endpoints.py; then
    echo "Feed test success."
else
    echo "Feed endpoint failure."
    exit 1  # Exit the script if there's a failure
fi

print_section "All tests complete."



