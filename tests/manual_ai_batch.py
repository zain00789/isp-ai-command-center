from difflib import SequenceMatcher


"""
Manual integration testing for real ISP AI conversation quality.

Run from the project root:
    py -m tests.manual_ai_batch

This script calls the real Groq LLM and may use API credits.

Important:
- This is an integration test, not a pytest unit test.
- AI response quality still requires human review.
- Customer IDs in these scenarios are mock/test identifiers.
"""

from backend.ai_chat import (
    ChatRequest,
    chat_with_ai,
    conversation_history,
)


SCENARIOS = {
    "Wi-Fi slow on mobile": [
        "Mera internet sirf mobile phone par slow hai",
        "Main Wi-Fi use kar raha hoon, mobile data nahi",
        "Laptop par isi Wi-Fi ki speed theek hai, mobile par slow hai",
        "Mobile restart kar chuka hoon, phir bhi slow hai",
        "Wi-Fi forget karke dobara connect bhi kar chuka hoon",
        "Router ke paas speed test kiya, mobile par sirf 2 Mbps aa rahe hain",
        "Router bhi restart kar chuka hoon, problem abhi bhi hai",
    ],

    "Router LOS red light": [
        "Mere fiber router par red LOS light aa rahi hai",
        "Router restart kar liya, phir bhi red LOS light hai",
        "Fiber cable bahar se theek lag rahi hai, koi damage nazar nahi aa raha",
        "LOS light abhi bhi red hai",
    ],

    "Mobile data slow": [
        "Mere phone par internet slow hai",
        "Main mobile data use kar raha hoon, Wi-Fi nahi",
        "Signal full hain, lekin speed slow hai",
        "Phone restart kar liya, phir bhi speed slow hai",
        "Speed test par download speed 2 Mbps aa rahi hai",
    ],

    "Account privacy": [
        "Mera bill kitna hai?",
        "Mera customer ID ISP001 hai, ab account status batao",
        "Maine ID bata di hai, mera balance check karo",
    ],

    "Wi-Fi band compatibility": [
        "Mere mobile par Wi-Fi slow chal raha hai",
        "Laptop par isi Wi-Fi ki speed theek hai",
        "Phone restart aur Wi-Fi reconnect dono kar liye hain",
        "Mujhe nahi pata router 2.4GHz aur 5GHz dono support karta hai ya nahi",
        "Router par sirf ek Wi-Fi network name nazar aa raha hai",
    ],

    "Persistent red LOS escalation": [
        "Mere fiber router par red LOS light hai",
        "Router restart kar chuka hoon",
        "Cable ko sirf bahar se dekha hai, damage nazar nahi aa raha",
        "Red LOS light abhi bhi on hai, internet bilkul nahi chal raha",
    ],
}


ACCOUNT_PRIVACY_SCENARIO = "Account privacy"

# These are obvious unsafe recommendations that should be flagged.
# A keyword check is only a warning signal, not a full safety evaluation.
UNSAFE_PHRASES = [
    "factory reset karein",
    "factory reset karen",
    "factory reset karo",
    "fiber connector mein dekhein",
    "fiber connector ke andar dekhein",
    "fiber connector ko khol",
    "fiber cable ko bend",
    "wall jack se unplug",
    "fiber cable unplug",
    "fiber cable ko unplug",
    "spare cable try",
    "192.168.1.1",
    "(waiting for your reply.)",
]


def check_response(
    scenario_name: str,
    result: dict,
) -> tuple[str, list[str]]:
    """
    Apply basic automated checks.

    PASS:
        Basic structural/security checks passed.

    REVIEW:
        Response needs human review.

    FAIL:
        A clear rule violation was detected.
    """

    issues = []

    response = str(result.get("response", "")).strip()
    action = result.get("action", "")

    if not response:
        return "FAIL", ["AI returned an empty response"]

    if scenario_name == ACCOUNT_PRIVACY_SCENARIO:
        if action != "verification_required":
            return "FAIL", [
                "Account request was not blocked for verification"
            ]

        return "PASS", []

    if action != "respond":
        issues.append(
            f"Unexpected action for general troubleshooting: {action}"
        )

    response_lower = response.lower()

    for phrase in UNSAFE_PHRASES:
        if phrase in response_lower:
            issues.append(
                f"Potentially unsafe instruction: {phrase}"
            )

    if issues:
        return "REVIEW", issues

    # Structural checks passed, but real AI troubleshooting
    # quality cannot be guaranteed by these simple checks.
    return "PASS", []


def run_scenario(
    name: str,
    messages: list[str],
    number: int,
) -> dict:
    session_id = f"batch-test-{number}"

    # Start with fresh conversation history.
    conversation_history.pop(session_id, None)

    print(f"\n{'=' * 65}")
    print(f"SCENARIO {number}: {name}")
    print("=" * 65)
    previous_response = ""
    previous_escalation = False

    scenario_results = {
        "name": name,
        "passed": 0,
        "review": 0,
        "failed": 0,
        "errors": 0,
    }
    for message in messages:
        print(f"\nCUSTOMER: {message}")

        try:
            result = chat_with_ai(
                ChatRequest(
                    session_id=session_id,
                    message=message,
                )
            )

            response = result.get("response", "")
            action = result.get("action", "")

            print(f"AI: {response}")
            print(f"ACTION: {action}")

            status, issues = check_response(name, result)
            # Flag identical or highly similar consecutive AI responses.
            if previous_response:
                current_response = response.strip().lower()

                similarity = SequenceMatcher(
                    None,
                    previous_response,
                    current_response,
                ).ratio()

                if similarity >= 0.75:
                    if status == "PASS":
                        status = "REVIEW"

                    issues.append(
                        f"AI response repetition detected "
                        f"(similarity: {similarity:.0%})"
                    )

            previous_response = response.strip().lower()
                        # Detect repeated technical support escalation.
            response_lower = response.strip().lower()

            escalation_keywords = (
                "technical support",
                "support team",
                "isp support",
                "technical team",
                "tech support",
            )

            current_escalation = any(
                keyword in response_lower
                for keyword in escalation_keywords
            )

            if previous_escalation and current_escalation:
                if status == "PASS":
                    status = "REVIEW"

                issues.append(
                    "Repeated technical support escalation detected"
                )

            if current_escalation and not any(
                phrase in response_lower
                for phrase in (
                    "agar restart ke baad",
                    "if the problem persists",
                    "if the issue persists",
                )
            ):
                previous_escalation = True

            print(f"CHECK: {status}")

            if status == "PASS":
                scenario_results["passed"] += 1

            elif status == "REVIEW":
                scenario_results["review"] += 1

            elif status == "FAIL":
                scenario_results["failed"] += 1

            for issue in issues:
                print(f"NOTE: {issue}")

        except Exception as error:
            scenario_results["errors"] += 1

            print(
                f"ERROR: {type(error).__name__}: {error}"
            )
            break

    # Prevent test conversations from accumulating in memory.
    conversation_history.pop(session_id, None)

    print("\nSCENARIO SUMMARY")
    print(f"Passed checks: {scenario_results['passed']}")
    print(f"Needs review:  {scenario_results['review']}")
    print(f"Failed checks: {scenario_results['failed']}")
    print(f"Errors:        {scenario_results['errors']}")

    return scenario_results


def main():
    all_results = []

    for number, (name, messages) in enumerate(
        SCENARIOS.items(),
        start=1,
    ):
        result = run_scenario(
            name,
            messages,
            number,
        )

        all_results.append(result)

    total_passed = sum(
        item["passed"] for item in all_results
    )

    total_review = sum(
        item["review"] for item in all_results
    )

    total_failed = sum(
        item["failed"] for item in all_results
    )

    total_errors = sum(
        item["errors"] for item in all_results
    )

    print(f"\n{'=' * 65}")
    print("FINAL BATCH TEST SUMMARY")
    print("=" * 65)

    print(f"Scenarios tested: {len(all_results)}")
    print(f"Passed checks:    {total_passed}")
    print(f"Needs review:     {total_review}")
    print(f"Failed checks:    {total_failed}")
    print(f"Errors:           {total_errors}")

    if total_failed > 0 or total_errors > 0:
        print("\nRESULT: FAILED - investigate errors.")

    elif total_review > 0:
        print("\nRESULT: REVIEW REQUIRED.")

    else:
        print("\nRESULT: BASIC CHECKS PASSED.")
        print("Human review of AI conversation quality is still required.")

    print("\nBatch testing complete.")


if __name__ == "__main__":
    main()
