from django.shortcuts import render


def home(request):
    quick_actions = [
        {
            "title": "Orders",
            "questions": [
                "Track an order from purchase to delivery.",
                "Update payment or billing details.",
                "Get help with gift cards and receipts.",
            ],
        },
        {
            "title": "Returns",
            "questions": [
                "Start a return or exchange online.",
                "Review refund timing and return policy.",
                "Report an item that arrived damaged.",
            ],
        },
        {
            "title": "Services",
            "questions": [
                "Book a virtual shopping session.",
                "Find a nearby store or service location.",
                "Learn about complimentary alterations.",
            ],
        },
        {
            "title": "Sizing",
            "questions": [
                "Use the size guide before ordering.",
                "Chat with an educator for fit support.",
            ],
        },
    ]
    contact_options = [
        {
            "eyebrow": "Fast support",
            "title": "Chat with us",
            "description": "Our virtual assistant is ready 24/7 and can connect you with a human during support hours.",
            "cta": "Start live chat",
        },
        {
            "eyebrow": "Expert guidance",
            "title": "Shop with a product expert",
            "description": "Get help with recommendations, fit questions, and placing your next order.",
            "cta": "Book a session",
        },
        {
            "eyebrow": "Still need help?",
            "title": "Send an email",
            "description": "Tell us what is going on and our team will follow up with the next best step.",
            "cta": "Email support",
        },
    ]
    context = {
        "quick_actions": quick_actions,
        "contact_options": contact_options,
    }
    return render(request, "pages/home.html", context)
