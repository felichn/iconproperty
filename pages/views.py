from django.shortcuts import render


def home(request):
    property_paths = [
        {
            "title": "Buy",
            "items": [
                "Compare curated homes by neighborhood, price, and lifestyle fit.",
                "Save listings that match your must-have details.",
                "Move from shortlist to showing with fewer steps.",
            ],
        },
        {
            "title": "Rent",
            "items": [
                "Find available spaces with clean filters and clear next steps.",
                "Review amenities, commute context, and lease highlights.",
                "Keep favorite properties organized in one place.",
            ],
        },
        {
            "title": "Sell",
            "items": [
                "Position your property with confident presentation.",
                "Understand comparable activity in your local market.",
                "Create a sharper launch plan from first look to listing.",
            ],
        },
        {
            "title": "Invest",
            "items": [
                "Scan opportunities with practical performance signals.",
                "Balance location, yield, and long-term upside.",
            ],
        },
    ]
    feature_cards = [
        {
            "eyebrow": "Curated search",
            "title": "Sharper property discovery",
            "description": "A focused browsing experience that highlights the homes and spaces worth a closer look.",
            "cta": "Browse homes",
        },
        {
            "eyebrow": "Market view",
            "title": "Local context at a glance",
            "description": "Neighborhood cues, price clarity, and property details arranged for quick comparison.",
            "cta": "View insights",
        },
        {
            "eyebrow": "Move-ready",
            "title": "Shortlists built for action",
            "description": "Keep decisions moving with saved spaces, priority notes, and clear paths to the next step.",
            "cta": "Start shortlist",
        },
    ]
    context = {
        "property_paths": property_paths,
        "feature_cards": feature_cards,
    }
    return render(request, "pages/home.html", context)
