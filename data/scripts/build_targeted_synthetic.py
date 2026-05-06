from pathlib import Path
import json

PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUT_PATH = PROJECT_ROOT / "data/processed/synthetic_clean.jsonl"


def make_rows() -> list[dict]:
    emergencies = [
        ("What should I do right away if my blood sugar drops and I feel shaky?",
         "If you feel shaky, sweaty, confused, or weak, check your blood sugar if you can. Take a quick sugar source like juice or glucose tablets. Wait 15 minutes, then recheck. If symptoms continue, repeat once and call for urgent help. Tell family how to support you."),
        ("When is low blood sugar an emergency that needs urgent care?",
         "Low blood sugar is an emergency if you are confused, cannot swallow safely, faint, or have seizures. A family member should call emergency services immediately. Do not force food into someone who is unconscious. After recovery, speak with your diabetes clinician to prevent repeat episodes."),
        ("How do I handle very high blood sugar with vomiting at home?",
         "Very high blood sugar with vomiting can become dangerous quickly. Drink water in small sips and check sugar often. If you cannot keep fluids down, feel drowsy, or have fast breathing, seek urgent care now. These signs may mean severe dehydration or diabetic emergency complications."),
        ("What warning signs mean I should go to the hospital for high blood sugar?",
         "Go to hospital if sugar stays very high, you have vomiting, belly pain, deep breathing, confusion, or severe weakness. These symptoms may signal a serious emergency. Do not delay. Keep your diabetes records and current medicines with you when traveling to care."),
        ("How can my family help if I have severe hypoglycemia at home?",
         "Family should learn your warning signs and emergency steps. If you are awake, they can give fast sugar and stay with you. If you become unconscious, they should call emergency services immediately. They should never force liquids into your mouth when you cannot swallow safely."),
        ("What should I do during sick days if I have type 2 diabetes?",
         "During illness, keep checking blood sugar more often and drink fluids regularly. Try small amounts of easy food if appetite is low. Rest and monitor for warning signs like vomiting, confusion, or very high sugars. Contact your care team early if symptoms worsen or persist."),
        ("How often should I monitor blood sugar when I am ill with fever?",
         "When sick, monitor blood sugar more frequently than usual because illness can push levels up or down. Record values and symptoms so your clinician can guide you. Seek urgent care if sugars stay extreme, you cannot drink fluids, or you become drowsy or confused."),
        ("What should I pack for diabetes emergencies while traveling?",
         "Pack glucose tablets, snacks, water, your medicine list, testing supplies, and emergency contact numbers. Keep items in hand luggage, not checked bags. Carry a diabetes ID card. If symptoms of low or high sugar appear, treat quickly and seek local urgent care when needed."),
        ("How should I store insulin safely during travel in hot weather?",
         "Keep insulin away from direct sun and extreme heat. Use an insulated pouch with cool packs, but avoid freezing. Check expiration and appearance before use. If insulin was exposed to high heat for long periods, seek replacement promptly and consult your clinician for safe continuity."),
        ("What should I do if I miss meals and feel symptoms of low sugar?",
         "If meals are delayed and you feel shaky, hungry, sweaty, or dizzy, treat low sugar quickly with a fast carbohydrate source. Recheck after 15 minutes if possible. Eat a follow-up snack once improved. Discuss meal planning and medication timing with your care team."),
        ("When should I call emergency services for diabetes symptoms?",
         "Call emergency services for unconsciousness, seizures, chest pain, severe confusion, or breathing difficulty. These signs require immediate medical help. Keep emergency numbers visible at home. Family members should know your diabetes history and where your supplies are stored."),
        ("Can dehydration trigger dangerous blood sugar problems?",
         "Yes, dehydration can worsen blood sugar instability and make emergencies more likely. Drink fluids through the day, especially during heat or illness. If you have persistent vomiting, reduced urination, or severe weakness, seek urgent care promptly to avoid serious complications."),
        ("What urgent signs should I watch for overnight with diabetes?",
         "Watch for sweating, restlessness, confusion, abnormal breathing, severe thirst, or repeated urination with weakness. If symptoms are severe or persistent, do not wait until morning. Seek urgent care. Keep quick sugar, water, and emergency contacts near your bedside."),
        ("How can I prepare a diabetes emergency plan for my household?",
         "Create a simple written plan with symptoms, first steps, emergency contacts, and nearby hospital details. Train family on low and high sugar warning signs. Store supplies in one known place. Review the plan regularly so everyone can act quickly during emergencies."),
        ("What should I do if my glucose meter fails during symptoms?",
         "If your meter fails and you have symptoms of low or high sugar, treat based on symptoms and seek help early. Use backup strips or a spare meter if available. Keep emergency snacks and water with you. Arrange meter replacement quickly to restore safe self-monitoring."),
    ]

    foot_care = [
        ("How can I check my feet daily if I have diabetes?",
         "Check both feet every day, including between toes and heel areas. Look for cuts, blisters, redness, swelling, or color changes. Use a mirror if needed. Wash gently, dry well, and moisturize dry skin, but not between toes. Report new wounds early to prevent complications."),
        ("When should a foot wound become urgent for a diabetic patient?",
         "A foot wound is urgent if it becomes red, warm, swollen, painful, foul-smelling, or starts draining pus. Fever or spreading redness needs immediate care. Do not wait for home remedies. Early treatment can prevent serious infection and reduce risk of hospitalization."),
        ("What shoes are safest for diabetic foot protection?",
         "Choose closed, well-fitted shoes with soft interiors and enough toe space. Avoid tight straps and hard seams that rub skin. Wear clean socks daily and inspect shoes before use for stones or rough edges. Proper footwear lowers injury risk and protects long-term foot health."),
        ("How should I care for cracked heels with diabetes?",
         "Wash feet gently, dry fully, and apply moisturizer to dry skin areas except between toes. Do not cut cracks yourself. Wear protective footwear indoors and outdoors. If cracks bleed, become painful, or look infected, seek professional care quickly to avoid deeper complications."),
        ("Is numbness in my feet a warning sign in diabetes?",
         "Yes, numbness may suggest nerve damage and raises injury risk because pain signals become weaker. Check feet daily and avoid walking barefoot. Use proper footwear and attend regular foot exams. Report numbness progression early so your care team can prevent worsening damage."),
        ("What should I do if I notice a blister on my diabetic foot?",
         "Do not pop the blister. Keep it clean and protected with a sterile dressing. Reduce pressure on that area and monitor for redness, swelling, or discharge. If healing is slow or signs of infection appear, seek clinical care promptly to prevent ulcer development."),
        ("How can I prevent diabetic foot ulcers at home?",
         "Prevent ulcers by daily foot checks, gentle washing, proper drying, and wearing protective shoes. Control blood sugar consistently and avoid barefoot walking. Trim nails carefully or get help if vision is poor. Seek early care for small injuries before they become serious."),
        ("When should I avoid self-treating corns or calluses in diabetes?",
         "Avoid self-cutting corns or using harsh chemicals because skin damage can lead to infection. Ask a trained clinician or podiatry service for safe management. If calluses become painful, red, or cracked, seek care early to prevent ulcers and protect mobility."),
        ("Why is foot care especially important in type 2 diabetes?",
         "Diabetes can reduce blood flow and nerve sensation, making minor injuries harder to feel and slower to heal. Without daily care, small wounds can become serious infections. Regular foot checks, safe footwear, and prompt treatment help prevent avoidable complications and amputation risk."),
        ("What should I do if my toenail area becomes red and painful?",
         "Clean and protect the area, avoid tight shoes, and monitor for worsening pain or discharge. Redness around nails may indicate infection, especially in diabetes. Seek professional foot assessment early rather than waiting. Early treatment lowers risk of deeper soft tissue involvement."),
        ("Can walking barefoot at home harm diabetic feet?",
         "Yes, walking barefoot increases risk of unnoticed cuts, burns, and puncture injuries. Because diabetes may reduce sensation, injuries can worsen before you notice them. Wear protective footwear indoors and outdoors. Check feet every evening for new marks or tender spots."),
        ("How often should I have a professional diabetic foot exam?",
         "Have a regular foot exam at least yearly, and more often if you have neuropathy, prior ulcers, or circulation problems. Professional checks find issues early. Combine clinic exams with daily home checks to reduce serious foot complications over time."),
        ("What are signs of poor circulation in diabetic feet?",
         "Signs include cold feet, color changes, slow-healing wounds, pain when walking, and weak pulses. Poor circulation can delay healing and raise ulcer risk. Report these symptoms promptly for vascular and diabetes review. Early action helps protect function and limb health."),
        ("How should I trim toenails safely with diabetes?",
         "Trim nails straight across with clean tools and avoid cutting corners deeply. File sharp edges gently to prevent skin injury. If vision is poor or nails are thick, ask a clinician for help. Safe nail care prevents ingrown nails and infection."),
        ("What should I do if my diabetic foot ulcer is not healing?",
         "If a foot ulcer is not improving, seek urgent diabetic foot care. Keep pressure off the wound, maintain clean dressings, and monitor for infection signs. Delayed healing needs professional assessment for blood flow, infection, and glucose control to prevent severe complications."),
    ]

    rows = []
    for q, a in emergencies:
        rows.append({"instruction": q, "input": "", "output": a, "topic": "emergencies", "source": "synthetic"})
    for q, a in foot_care:
        rows.append({"instruction": q, "input": "", "output": a, "topic": "foot_care", "source": "synthetic"})
    return rows


def main() -> None:
    rows = make_rows()
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUT_PATH.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print("Wrote targeted synthetic rows:", len(rows))
    print("Saved:", OUT_PATH)


if __name__ == "__main__":
    main()
