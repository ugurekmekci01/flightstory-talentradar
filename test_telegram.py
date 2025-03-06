import send_telegram  # Import the send_telegram module

# Example function to test sending a message and image
def test_send_telegram():
    message = "Hello from the Telegram bot!"
    image_path = "test.jpeg"  # Replace this with the path to a .png image on your system
    
    # Call the function to send a message and image by passing them as arguments
    send_telegram.execute_send_telegram(message, image_path)

# Run the test
if __name__ == "__main__":
    test_send_telegram()
