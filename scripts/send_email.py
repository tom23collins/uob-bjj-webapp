from flask import Flask, request, render_template
from flask_mail import Mail, Message

def send_welcome_email(app, mail, recipient_email, first_name):
    try:
        # Create a new email message
        msg = Message(
            subject="Welcome to the UoB BJJ Signup App!",
            sender=app.config.get('MAIL_USERNAME'),
            recipients=[recipient_email]
        )

        # Plain-text version
        msg.body = "Thank you for signing up for our service. We're excited to have you!"

        # Load HTML content from the file using render_template
        msg.html = render_template('welcome_email.html',
                                   first_name=first_name)

        # Send the email
        mail.send(msg)

    except Exception as e:
        print(f"Failed to send email: {e}")
