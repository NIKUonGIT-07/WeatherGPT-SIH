def build_decision_response(decisions, category=None):

    response = "Decision Support\n"
    response += "────────────────────────\n\n"

    for decision in decisions:

        if category is not None:

            if decision["title"].lower().startswith(category.lower()) is False:
                continue

        response += f"""{decision["title"]}
• Status : {decision["status"]}
• Reason : {decision["reason"]}
• Advice : {decision["advice"]}

"""

    return response