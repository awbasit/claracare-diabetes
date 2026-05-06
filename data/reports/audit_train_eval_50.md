# Train/Eval Manual Audit (50 Samples)

Review this before any SFT run.

- Train samples: 30
- Eval samples: 20

## Sample 1
- Split: train
- Source: hf_diabetes_qa
- Topic: blood_sugar_monitoring
- Instruction: Can you explain the autoimmune process involved in the development of type 1 diabetes?
- Output: Type 1 diabetes is an autoimmune disease where the body's immune system mistakenly attacks and destroys the insulin-producing cells (beta cells) in the pancreas. This leads to a deficiency in insulin production, which is essential for regulating blood sugar levels.
- Checklist:
  - Readable and simple? [TODO]
  - Diabetes-centered? [TODO]
  - Tone consistent with ClaraCare? [TODO]
  - Unsafe advice or dosage? [TODO]
  - Duplicative/near-duplicate? [TODO]
  - Keep? [TODO]
- Reviewer note: TODO

## Sample 2
- Split: train
- Source: hf_diabetes_qa
- Topic: other_diabetes
- Instruction: What is the significance of understanding the historical advancements in diabetes treatment and research?
- Output: Appreciating the historical progress in diabetes care highlights the ongoing efforts to improve treatments, prevention strategies, and the lives of individuals living with the condition.
- Checklist:
  - Readable and simple? [TODO]
  - Diabetes-centered? [TODO]
  - Tone consistent with ClaraCare? [TODO]
  - Unsafe advice or dosage? [TODO]
  - Duplicative/near-duplicate? [TODO]
  - Keep? [TODO]
- Reviewer note: TODO

## Sample 3
- Split: eval
- Source: synthetic
- Topic: how to manage diabetes on a low income in West Africa
- Instruction: How can I manage my diabetes when I have little money?
- Output: Managing diabetes on a low income can be tough. Focus on eating healthy, low-cost foods like beans, vegetables, and fruits. Regular exercise is free and helps too. Also, keep track of your blood sugar. Always talk to your doctor for advice.
- Checklist:
  - Readable and simple? [TODO]
  - Diabetes-centered? [TODO]
  - Tone consistent with ClaraCare? [TODO]
  - Unsafe advice or dosage? [TODO]
  - Duplicative/near-duplicate? [TODO]
  - Keep? [TODO]
- Reviewer note: TODO

## Sample 4
- Split: train
- Source: hf_diabetes_qa
- Topic: blood_sugar_monitoring
- Instruction: Can you explain the potential risks of not carrying a carbohydrate source during exercise for someone with diabetes?
- Output: Without readily available carbohydrates, individuals with diabetes could experience a drop in blood sugar levels, leading to hypoglycemia. Symptoms include dizziness, confusion, weakness, and even loss of consciousness, making it crucial to have a quick source of glucose on hand.
- Checklist:
  - Readable and simple? [TODO]
  - Diabetes-centered? [TODO]
  - Tone consistent with ClaraCare? [TODO]
  - Unsafe advice or dosage? [TODO]
  - Duplicative/near-duplicate? [TODO]
  - Keep? [TODO]
- Reviewer note: TODO

## Sample 5
- Split: train
- Source: hf_diabetes_qa
- Topic: blood_sugar_monitoring
- Instruction: What is the primary advantage of using a pill box specifically designed for diabetes medication?
- Output: A pill box tailored for diabetes medication ensures that the correct dosage and timing of medications are followed, leading to better control of blood sugar levels.
- Checklist:
  - Readable and simple? [TODO]
  - Diabetes-centered? [TODO]
  - Tone consistent with ClaraCare? [TODO]
  - Unsafe advice or dosage? [TODO]
  - Duplicative/near-duplicate? [TODO]
  - Keep? [TODO]
- Reviewer note: TODO

## Sample 6
- Split: train
- Source: real
- Topic: medication
- Instruction: Can the medication for hypertension cause baldness ? Age: 69, Male, Hypertension and Type II DM on oral anti diatetes/hypertensive drugs (Glebenclamide 2.5 mg BD, Metformin 500mgm BD and Ramipril 5mgm OD, Atenolol 50 mgm OD, amlidopine 5 mgm OD). Both conditions under control. Can any of these drugs cause baldness? I have been rapidly balding of late.
- Output: welcome to healthcaremagic.. its not your medication that is causing you baldness,it is because of your stress and age which is a normal phenomenon..people lose hair cos of age..if its very rapid get a complete blood test to rule out infections..
- Checklist:
  - Readable and simple? [TODO]
  - Diabetes-centered? [TODO]
  - Tone consistent with ClaraCare? [TODO]
  - Unsafe advice or dosage? [TODO]
  - Duplicative/near-duplicate? [TODO]
  - Keep? [TODO]
- Reviewer note: TODO

## Sample 7
- Split: train
- Source: hf_diabetes_qa
- Topic: diet_lifestyle
- Instruction: What are some examples of healthy fats that should be included in a diabetes-friendly diet?
- Output: Healthy fats for a diabetes-friendly diet include monounsaturated fats like those found in olive oil, avocados, nuts, and seeds, as well as polyunsaturated fats like those in fatty fish, flaxseeds, and walnuts.
- Checklist:
  - Readable and simple? [TODO]
  - Diabetes-centered? [TODO]
  - Tone consistent with ClaraCare? [TODO]
  - Unsafe advice or dosage? [TODO]
  - Duplicative/near-duplicate? [TODO]
  - Keep? [TODO]
- Reviewer note: TODO

## Sample 8
- Split: train
- Source: hf_diabetes_qa
- Topic: blood_sugar_monitoring
- Instruction: What specific advice should a person with diabetes receive regarding alcohol consumption from a doctor?
- Output: A doctor will assess individual factors like medication, blood sugar control, and overall health to provide personalized guidance on safe alcohol limits, timing, and potential risks for individuals with diabetes.
- Checklist:
  - Readable and simple? [TODO]
  - Diabetes-centered? [TODO]
  - Tone consistent with ClaraCare? [TODO]
  - Unsafe advice or dosage? [TODO]
  - Duplicative/near-duplicate? [TODO]
  - Keep? [TODO]
- Reviewer note: TODO

## Sample 9
- Split: eval
- Source: synthetic
- Topic: common side effects of metformin in simple language
- Instruction: What are the common side effects of metformin?
- Output: Metformin can cause some side effects. You might feel stomach aches or upset stomach. Some people have diarrhea. These effects usually go away over time. Drink plenty of water and eat small meals. Always talk to your doctor if you feel unwell.
- Checklist:
  - Readable and simple? [TODO]
  - Diabetes-centered? [TODO]
  - Tone consistent with ClaraCare? [TODO]
  - Unsafe advice or dosage? [TODO]
  - Duplicative/near-duplicate? [TODO]
  - Keep? [TODO]
- Reviewer note: TODO

## Sample 10
- Split: eval
- Source: synthetic
- Topic: what happens when blood sugar stays high for too long
- Instruction: What happens when my blood sugar stays high for too long?
- Output: When blood sugar stays high for too long, it can cause serious problems. You may feel tired and thirsty. High blood sugar can hurt your eyes, kidneys, and nerves. It can also lead to heart issues. It is important to talk to your doctor for advice.
- Checklist:
  - Readable and simple? [TODO]
  - Diabetes-centered? [TODO]
  - Tone consistent with ClaraCare? [TODO]
  - Unsafe advice or dosage? [TODO]
  - Duplicative/near-duplicate? [TODO]
  - Keep? [TODO]
- Reviewer note: TODO

## Sample 11
- Split: eval
- Source: synthetic
- Topic: how to get support from family when living with diabetes
- Instruction: How can I get help from my family while living with diabetes?
- Output: Talk to your family about your diabetes. Share what you need from them. Ask them to join you in healthy meals or exercise. Let them know how they can help you feel better. Support makes managing diabetes easier. Always consult a doctor for personal advice.
- Checklist:
  - Readable and simple? [TODO]
  - Diabetes-centered? [TODO]
  - Tone consistent with ClaraCare? [TODO]
  - Unsafe advice or dosage? [TODO]
  - Duplicative/near-duplicate? [TODO]
  - Keep? [TODO]
- Reviewer note: TODO

## Sample 12
- Split: eval
- Source: synthetic
- Topic: how to get support from family when living with diabetes
- Instruction: How can I get my family to support me while I live with diabetes?
- Output: Talk openly with your family about your diabetes. Explain what it means for you. Share your needs and feelings. Ask them for help with meals or exercise. Encourage them to learn more about diabetes. Their support can really help you.
- Checklist:
  - Readable and simple? [TODO]
  - Diabetes-centered? [TODO]
  - Tone consistent with ClaraCare? [TODO]
  - Unsafe advice or dosage? [TODO]
  - Duplicative/near-duplicate? [TODO]
  - Keep? [TODO]
- Reviewer note: TODO

## Sample 13
- Split: train
- Source: hf_diabetes_qa
- Topic: emotional_support
- Instruction: What role does seeking support from others play in promoting a positive body image and self-esteem for individuals with diabetes?
- Output: Seeking support from loved ones or mental health professionals can be a valuable resource for individuals with diabetes in maintaining a positive body image and self-esteem, alongside focusing on overall health and well-being and engaging in fulfilling activities.
- Checklist:
  - Readable and simple? [TODO]
  - Diabetes-centered? [TODO]
  - Tone consistent with ClaraCare? [TODO]
  - Unsafe advice or dosage? [TODO]
  - Duplicative/near-duplicate? [TODO]
  - Keep? [TODO]
- Reviewer note: TODO

## Sample 14
- Split: train
- Source: hf_diabetes_qa
- Topic: blood_sugar_monitoring
- Instruction: How do kidney function tests help in the treatment and management of diabetic kidney disease?
- Output: Kidney function tests play a crucial role in the management of diabetic kidney disease. They provide information about the severity of kidney damage and the effectiveness of treatment interventions. By monitoring kidney function over time, healthcare providers can adjust treatment plans, manage blood sugar levels, and minimize further kidney damage.
- Checklist:
  - Readable and simple? [TODO]
  - Diabetes-centered? [TODO]
  - Tone consistent with ClaraCare? [TODO]
  - Unsafe advice or dosage? [TODO]
  - Duplicative/near-duplicate? [TODO]
  - Keep? [TODO]
- Reviewer note: TODO

## Sample 15
- Split: train
- Source: hf_diabetes_qa
- Topic: blood_sugar_monitoring
- Instruction: Besides medications, what else should be included in a diabetes emergency kit to ensure proper care in case of a disaster?
- Output: In addition to medications, a diabetes emergency kit should include a blood glucose meter, lancets, testing strips, a glucagon kit, glucose tablets or other fast-acting carbohydrates, antibiotic cream, a copy of your medical information, and emergency contact numbers.
- Checklist:
  - Readable and simple? [TODO]
  - Diabetes-centered? [TODO]
  - Tone consistent with ClaraCare? [TODO]
  - Unsafe advice or dosage? [TODO]
  - Duplicative/near-duplicate? [TODO]
  - Keep? [TODO]
- Reviewer note: TODO

## Sample 16
- Split: train
- Source: hf_diabetes_qa
- Topic: blood_sugar_monitoring
- Instruction: What are the key steps individuals with diabetes should take to manage their blood sugar levels during long car journeys?
- Output: Individuals with diabetes should monitor their blood glucose levels before starting the trip and every two hours while driving. They should also pack essential diabetes supplies, such as insulin, glucose tablets, and a glucagon kit, in case of emergencies. Regular breaks are crucial to prevent hypoglycemia, allowing for stretching, hydration, and glucose checks.
- Checklist:
  - Readable and simple? [TODO]
  - Diabetes-centered? [TODO]
  - Tone consistent with ClaraCare? [TODO]
  - Unsafe advice or dosage? [TODO]
  - Duplicative/near-duplicate? [TODO]
  - Keep? [TODO]
- Reviewer note: TODO

## Sample 17
- Split: eval
- Source: synthetic
- Topic: how to keep a simple diabetes diary at home
- Instruction: How can I keep a simple diabetes diary at home?
- Output: You can keep a diabetes diary by writing down your daily blood sugar levels. Note what you eat and your activities. Include how you feel and any medication taken. This helps you and your doctor understand your diabetes better. Remember to show it to your doctor.
- Checklist:
  - Readable and simple? [TODO]
  - Diabetes-centered? [TODO]
  - Tone consistent with ClaraCare? [TODO]
  - Unsafe advice or dosage? [TODO]
  - Duplicative/near-duplicate? [TODO]
  - Keep? [TODO]
- Reviewer note: TODO

## Sample 18
- Split: train
- Source: hf_diabetes_qa
- Topic: medication
- Instruction: How can medication regimens be adjusted to make it easier for individuals with diabetes to stick to their treatment plan?
- Output: Simplifying medication regimens by reducing the number of medications or doses, consolidating medications into a single daily dose, or using extended-release formulations can improve adherence.
- Checklist:
  - Readable and simple? [TODO]
  - Diabetes-centered? [TODO]
  - Tone consistent with ClaraCare? [TODO]
  - Unsafe advice or dosage? [TODO]
  - Duplicative/near-duplicate? [TODO]
  - Keep? [TODO]
- Reviewer note: TODO

## Sample 19
- Split: train
- Source: hf_diabetes_qa
- Topic: other_diabetes
- Instruction: How do vaccinations benefit individuals with diabetes, considering their weakened immune systems?
- Output: Vaccinations strengthen the immune system by introducing a weakened or inactive form of the virus or bacteria. This allows the body to develop immunity without experiencing the full-blown disease, which is crucial for individuals with diabetes who are more susceptible to infections.
- Checklist:
  - Readable and simple? [TODO]
  - Diabetes-centered? [TODO]
  - Tone consistent with ClaraCare? [TODO]
  - Unsafe advice or dosage? [TODO]
  - Duplicative/near-duplicate? [TODO]
  - Keep? [TODO]
- Reviewer note: TODO

## Sample 20
- Split: eval
- Source: synthetic
- Topic: how portion size affects blood sugar levels
- Instruction: How does the size of my food portions affect my blood sugar levels?
- Output: Eating too much food at once can raise your blood sugar. When you eat large portions, your body has to work harder to manage sugar. Smaller portions can help keep your blood sugar stable. Always talk to your doctor about your meal sizes.
- Checklist:
  - Readable and simple? [TODO]
  - Diabetes-centered? [TODO]
  - Tone consistent with ClaraCare? [TODO]
  - Unsafe advice or dosage? [TODO]
  - Duplicative/near-duplicate? [TODO]
  - Keep? [TODO]
- Reviewer note: TODO

## Sample 21
- Split: eval
- Source: synthetic
- Topic: why blood sugar rises after eating
- Instruction: Why does my blood sugar go up after I eat?
- Output: When you eat food, your body breaks it down into sugar. This sugar enters your blood. Your blood sugar level rises because your body is using sugar for energy. Some foods raise blood sugar more than others. It's important to talk to your doctor about your diet.
- Checklist:
  - Readable and simple? [TODO]
  - Diabetes-centered? [TODO]
  - Tone consistent with ClaraCare? [TODO]
  - Unsafe advice or dosage? [TODO]
  - Duplicative/near-duplicate? [TODO]
  - Keep? [TODO]
- Reviewer note: TODO

## Sample 22
- Split: eval
- Source: hf_diabetes_qa
- Topic: diabetes_basics
- Instruction: What are the key lifestyle changes that the DPP found to be effective in preventing type 2 diabetes?
- Output: The DPP highlighted the importance of diet and physical activity as key lifestyle changes that contributed to a significant reduction in the risk of type 2 diabetes, especially when combined to achieve modest weight loss.
- Checklist:
  - Readable and simple? [TODO]
  - Diabetes-centered? [TODO]
  - Tone consistent with ClaraCare? [TODO]
  - Unsafe advice or dosage? [TODO]
  - Duplicative/near-duplicate? [TODO]
  - Keep? [TODO]
- Reviewer note: TODO

## Sample 23
- Split: train
- Source: real
- Topic: diet_lifestyle
- Instruction: What treatment can I take for a diabetic person who is suffering from psoriasis ? My wife has been suffering from chronic psoriasis for a long time (15 years). She is 48 years old with two children. Her weight is 86 Kg with 5 feet 3 inches height. She also suffers from diabetics. I would like to meet you for her treatment . Would you please suggest me when and how I can approach you? What is the first treatment? would you please let me know in My email address abdulmaleque@yahoo.com with regards abdulmaleque@yahoo.com
- Output: hii welcome to health care magic. i went through your case,i feel that homoeopathic medicines would be of great help. coz psoriasis being a chronic immune mediated disease that appears on the skin, well u have not specified as whr is the psoriasis affection as such,coz there are different types of them.Homoeopathy has well defined German origin medicines that would prove effective if u take it on a regular basis and following up the necessary diet and regimen.
- Checklist:
  - Readable and simple? [TODO]
  - Diabetes-centered? [TODO]
  - Tone consistent with ClaraCare? [TODO]
  - Unsafe advice or dosage? [TODO]
  - Duplicative/near-duplicate? [TODO]
  - Keep? [TODO]
- Reviewer note: TODO

## Sample 24
- Split: train
- Source: hf_diabetes_qa
- Topic: blood_sugar_monitoring
- Instruction: How does an insulin pump differ from traditional insulin injections, and what advantages does it offer?
- Output: Unlike traditional injections, which deliver a fixed dose of insulin at specific times, insulin pumps provide a continuous, customizable flow of insulin. This enables more precise blood glucose control, reducing the risk of both high and low blood sugar levels, and allowing for greater freedom in daily routines.
- Checklist:
  - Readable and simple? [TODO]
  - Diabetes-centered? [TODO]
  - Tone consistent with ClaraCare? [TODO]
  - Unsafe advice or dosage? [TODO]
  - Duplicative/near-duplicate? [TODO]
  - Keep? [TODO]
- Reviewer note: TODO

## Sample 25
- Split: eval
- Source: synthetic
- Topic: how diabetes affects the feet and why foot care matters
- Instruction: How does diabetes affect my feet and why should I take care of them?
- Output: Diabetes can cause nerve damage and poor blood flow to your feet. This can make it hard to feel injuries or sores. If not taken care of, these can turn into serious infections. Regular foot care is very important to prevent problems.
- Checklist:
  - Readable and simple? [TODO]
  - Diabetes-centered? [TODO]
  - Tone consistent with ClaraCare? [TODO]
  - Unsafe advice or dosage? [TODO]
  - Duplicative/near-duplicate? [TODO]
  - Keep? [TODO]
- Reviewer note: TODO

## Sample 26
- Split: train
- Source: hf_diabetes_qa
- Topic: medication
- Instruction: What steps can individuals with diabetes take to protect their insulin from extreme temperatures during travel?
- Output: Use insulated bags to store insulin, keep it out of direct sunlight, and avoid placing it in checked baggage, as this can expose it to extreme temperatures that may damage the medication.
- Checklist:
  - Readable and simple? [TODO]
  - Diabetes-centered? [TODO]
  - Tone consistent with ClaraCare? [TODO]
  - Unsafe advice or dosage? [TODO]
  - Duplicative/near-duplicate? [TODO]
  - Keep? [TODO]
- Reviewer note: TODO

## Sample 27
- Split: eval
- Source: synthetic
- Topic: what to eat before and after exercise with diabetes
- Instruction: What should I eat before and after exercising with diabetes?
- Output: Before exercise, eat something light and healthy. A small banana or a piece of whole grain bread is good. After exercising, have a meal with protein and carbs. Examples are chicken with brown rice or beans with vegetables. Always talk to your doctor for personal advice.
- Checklist:
  - Readable and simple? [TODO]
  - Diabetes-centered? [TODO]
  - Tone consistent with ClaraCare? [TODO]
  - Unsafe advice or dosage? [TODO]
  - Duplicative/near-duplicate? [TODO]
  - Keep? [TODO]
- Reviewer note: TODO

## Sample 28
- Split: train
- Source: real
- Topic: diet_lifestyle
- Instruction: What treatment do you suggest for pain in left shoulder? my dad 79 years old high bloodpressure diabetic just yesterday found out had cellulitis on keflex 500 already had 6 pills has a pain in left shoulder took bloodpressure 240 over 150 had squad come went to 204/150 want to know if keflex can raise it
- Output: Hi and thank you so much for this query.I am so sorry to hear about this cellulitis. Keflex cannot cause this sudden and alarming increase in blood pressure. I will suggest that you get your father to the emergency room because these numbers are very high and need immediate attention to avoid related complications like stroke, heart, kidney damages, etc.Cellulitis in diabetics should be approached with full force because of the fear of severe complications. If the improvement is not remarkable withing 48hours, please talk to his treating doctor.I hope this helps. I wish you well.Dr. Ivo, D.
- Checklist:
  - Readable and simple? [TODO]
  - Diabetes-centered? [TODO]
  - Tone consistent with ClaraCare? [TODO]
  - Unsafe advice or dosage? [TODO]
  - Duplicative/near-duplicate? [TODO]
  - Keep? [TODO]
- Reviewer note: TODO

## Sample 29
- Split: eval
- Source: hf_diabetes_qa
- Topic: diet_lifestyle
- Instruction: How can public health policies contribute to creating healthier environments that support diabetes prevention?
- Output: Public health policies can play a crucial role by promoting access to healthy and affordable food options, encouraging physical activity through infrastructure development and public spaces, regulating food labeling and advertising, and implementing policies that discourage tobacco use and excessive alcohol consumption.
- Checklist:
  - Readable and simple? [TODO]
  - Diabetes-centered? [TODO]
  - Tone consistent with ClaraCare? [TODO]
  - Unsafe advice or dosage? [TODO]
  - Duplicative/near-duplicate? [TODO]
  - Keep? [TODO]
- Reviewer note: TODO

## Sample 30
- Split: eval
- Source: hf_diabetes_qa
- Topic: emotional_support
- Instruction: How can individuals with diabetes prioritize their mental well-being and maintain a positive self-perception in the context of a chronic condition?
- Output: Individuals with diabetes can cultivate a positive self-image and self-esteem by focusing on overall health and well-being, engaging in activities that bring joy and fulfillment, and seeking support from loved ones or mental health professionals.
- Checklist:
  - Readable and simple? [TODO]
  - Diabetes-centered? [TODO]
  - Tone consistent with ClaraCare? [TODO]
  - Unsafe advice or dosage? [TODO]
  - Duplicative/near-duplicate? [TODO]
  - Keep? [TODO]
- Reviewer note: TODO

## Sample 31
- Split: train
- Source: hf_diabetes_qa
- Topic: medication
- Instruction: What is the primary purpose of a doctor's letter when traveling with diabetes, particularly during air travel?
- Output: The main purpose of a doctor's letter is to provide clear and concise documentation about the necessity of carrying diabetes medications and supplies. This helps facilitate smooth airport security checks and eliminates any potential issues or misunderstandings.
- Checklist:
  - Readable and simple? [TODO]
  - Diabetes-centered? [TODO]
  - Tone consistent with ClaraCare? [TODO]
  - Unsafe advice or dosage? [TODO]
  - Duplicative/near-duplicate? [TODO]
  - Keep? [TODO]
- Reviewer note: TODO

## Sample 32
- Split: eval
- Source: synthetic
- Topic: how stress raises blood sugar and what to do about it
- Instruction: How does stress raise my blood sugar and what can I do about it?
- Output: Stress can make your body release more sugar into the blood. This can raise your blood sugar levels. To help with stress, try deep breathing or gentle exercise like walking. Talking to a friend or a doctor can also help. Always check with your doctor for advice.
- Checklist:
  - Readable and simple? [TODO]
  - Diabetes-centered? [TODO]
  - Tone consistent with ClaraCare? [TODO]
  - Unsafe advice or dosage? [TODO]
  - Duplicative/near-duplicate? [TODO]
  - Keep? [TODO]
- Reviewer note: TODO

## Sample 33
- Split: eval
- Source: synthetic
- Topic: safe exercises for someone newly diagnosed with diabetes
- Instruction: What safe exercises can I do after being diagnosed with diabetes?
- Output: It's great that you want to be active! Walking is a safe and easy exercise. You can also try biking or swimming. Start slowly and listen to your body. Always talk to your doctor before starting any new exercise plan.
- Checklist:
  - Readable and simple? [TODO]
  - Diabetes-centered? [TODO]
  - Tone consistent with ClaraCare? [TODO]
  - Unsafe advice or dosage? [TODO]
  - Duplicative/near-duplicate? [TODO]
  - Keep? [TODO]
- Reviewer note: TODO

## Sample 34
- Split: train
- Source: hf_diabetes_qa
- Topic: diabetes_basics
- Instruction: What distinguishes prediabetes from type 2 diabetes?
- Output: Prediabetes is characterized by higher-than-normal blood glucose levels, but not high enough to be classified as diabetes. It increases the risk of developing type 2 diabetes, heart disease, and stroke.
- Checklist:
  - Readable and simple? [TODO]
  - Diabetes-centered? [TODO]
  - Tone consistent with ClaraCare? [TODO]
  - Unsafe advice or dosage? [TODO]
  - Duplicative/near-duplicate? [TODO]
  - Keep? [TODO]
- Reviewer note: TODO

## Sample 35
- Split: eval
- Source: hf_diabetes_qa
- Topic: medication
- Instruction: Question: What are the primary methods of administering diabetes medications?
- Output: Diabetes medications are typically administered orally in pill form or via injection, often referred to as 'shots'.
- Checklist:
  - Readable and simple? [TODO]
  - Diabetes-centered? [TODO]
  - Tone consistent with ClaraCare? [TODO]
  - Unsafe advice or dosage? [TODO]
  - Duplicative/near-duplicate? [TODO]
  - Keep? [TODO]
- Reviewer note: TODO

## Sample 36
- Split: train
- Source: hf_diabetes_qa
- Topic: other_diabetes
- Instruction: How has the understanding of type 1 diabetes evolved over time?
- Output: The understanding of type 1 diabetes has evolved, and the term 'juvenile diabetes' is no longer widely used. It is now understood that type 1 diabetes can occur at any age, not just in youth.
- Checklist:
  - Readable and simple? [TODO]
  - Diabetes-centered? [TODO]
  - Tone consistent with ClaraCare? [TODO]
  - Unsafe advice or dosage? [TODO]
  - Duplicative/near-duplicate? [TODO]
  - Keep? [TODO]
- Reviewer note: TODO

## Sample 37
- Split: train
- Source: real
- Topic: diet_lifestyle
- Instruction: What causes bad body odor in a diabetic person? Hi Dr.,my mom is diabectic on insullin and 4 blood pressure pills ,on diladid for pain for spinal cord,theses medicines have been used for years with the exception of the diliadid for pain ,shes been on every pain killer there is almost and still has chronic pain ,however the question is ,...lately she has this terrible foul odor thats unbearable coming from her skin...whats going on ?please tell me where to start,its breaking my heart...
- Output: Hi..Thanks for the query..Well, medications can be a cause for bad body odour as well as uncontrolled diabetes causing ketoacidosis can also cause bad smell from breath and even body..Certain other causes like poor maintenance of hygiene, thyroid disorders and liver or kidney disorders can be a cause..So she needs a thorough evaluation for confirmation of the underlying cause so that appropriate treatment can be done..For now she should maintain a good body hygiene, use aromatic oils and soaps for bathing and also she can use deodorants for masking bad smell..Hope this helps..Regards..
- Checklist:
  - Readable and simple? [TODO]
  - Diabetes-centered? [TODO]
  - Tone consistent with ClaraCare? [TODO]
  - Unsafe advice or dosage? [TODO]
  - Duplicative/near-duplicate? [TODO]
  - Keep? [TODO]
- Reviewer note: TODO

## Sample 38
- Split: eval
- Source: hf_diabetes_qa
- Topic: emotional_support
- Instruction: Are there any online resources that can help me learn more about diabetes management and connect with others who have diabetes?
- Output: Yes, there are many online resources specifically designed for individuals with diabetes. You can find diabetes management apps, online communities, and educational websites from reputable organizations like the American Diabetes Association and the NIDDK. These platforms provide information, support, and a sense of community for those living with diabetes.
- Checklist:
  - Readable and simple? [TODO]
  - Diabetes-centered? [TODO]
  - Tone consistent with ClaraCare? [TODO]
  - Unsafe advice or dosage? [TODO]
  - Duplicative/near-duplicate? [TODO]
  - Keep? [TODO]
- Reviewer note: TODO

## Sample 39
- Split: train
- Source: hf_diabetes_qa
- Topic: blood_sugar_monitoring
- Instruction: Besides managing blood sugar, what other health benefits can individuals with diabetes expect from medical nutrition therapy?
- Output: In addition to blood sugar control, medical nutrition therapy can offer numerous other health benefits for individuals with diabetes. It can help them achieve and maintain a healthy weight, lower blood pressure and cholesterol levels, and reduce the risk of developing heart disease and other cardiovascular complications. By focusing on a balanced and nutritious diet, individuals can improve their overall health and well-being.
- Checklist:
  - Readable and simple? [TODO]
  - Diabetes-centered? [TODO]
  - Tone consistent with ClaraCare? [TODO]
  - Unsafe advice or dosage? [TODO]
  - Duplicative/near-duplicate? [TODO]
  - Keep? [TODO]
- Reviewer note: TODO

## Sample 40
- Split: train
- Source: hf_diabetes_qa
- Topic: other_diabetes
- Instruction: Can you elaborate on the role of collaboration between individuals with diabetes and their healthcare providers in empowering patients to make informed decisions?
- Output: Collaboration is key. Individuals with diabetes should feel comfortable asking questions, sharing their concerns, and working together with their healthcare providers to create a personalized treatment plan. This partnership ensures that decisions are made based on the individual's needs, preferences, and values, leading to greater empowerment and improved health outcomes.
- Checklist:
  - Readable and simple? [TODO]
  - Diabetes-centered? [TODO]
  - Tone consistent with ClaraCare? [TODO]
  - Unsafe advice or dosage? [TODO]
  - Duplicative/near-duplicate? [TODO]
  - Keep? [TODO]
- Reviewer note: TODO

## Sample 41
- Split: eval
- Source: hf_diabetes_qa
- Topic: other_diabetes
- Instruction: Why is it important for individuals with diabetes to use the 'Tests, Exams, and Vaccines to Get at Least Once or Twice a Year' chart?
- Output: The chart serves as a valuable resource for individuals with diabetes, helping them stay informed about essential medical procedures and ensuring they receive the necessary care to manage their condition effectively.
- Checklist:
  - Readable and simple? [TODO]
  - Diabetes-centered? [TODO]
  - Tone consistent with ClaraCare? [TODO]
  - Unsafe advice or dosage? [TODO]
  - Duplicative/near-duplicate? [TODO]
  - Keep? [TODO]
- Reviewer note: TODO

## Sample 42
- Split: train
- Source: hf_diabetes_qa
- Topic: other_diabetes
- Instruction: How does diabetes impact the global economy?
- Output: Diabetes has a substantial impact on the global economy due to increased healthcare costs associated with managing the disease. Additionally, lost productivity due to illness and disability among individuals with diabetes further strains economic resources.
- Checklist:
  - Readable and simple? [TODO]
  - Diabetes-centered? [TODO]
  - Tone consistent with ClaraCare? [TODO]
  - Unsafe advice or dosage? [TODO]
  - Duplicative/near-duplicate? [TODO]
  - Keep? [TODO]
- Reviewer note: TODO

## Sample 43
- Split: train
- Source: real
- Topic: exercise
- Instruction: What causes high blood pressure? my blood pressure is 144/94. I m a diabetic and I do take hbp pills. I have family members staying with me that won t leave. I feel like they are the one that keep my pressure up. I hate to come home after work. Do you think this could be part of my problem? I m fine at work considering I work with children.
- Output: hello, Stress can certainly increase the bp, as the reason for stress could not be omitted, we need to optimize the medicine. You should have a healthy lifestyle like avoiding fatty, oily and high calorie diet. Have low salt diet and monitor blood pressure regularly thrice a day for one week then once or twice a week. If bp is persistently more than 140/90 mmhg, then medicine needs to be increased and bp should preferably be below 130/85. Regular exercises like brisk walking, jogging according your capacity atleast 30 min a day and 5 days a week. Lots of green leafy vegetables, fruits, fish once or twice a week, avoid meat. Avoid smoking and alcohol if any. There shouldn't abdominal fat deposition or obesity. Get your lipid profile tested once.. If possible, try relaxation techniques like deep breathing and yoga to relieve stress.
- Checklist:
  - Readable and simple? [TODO]
  - Diabetes-centered? [TODO]
  - Tone consistent with ClaraCare? [TODO]
  - Unsafe advice or dosage? [TODO]
  - Duplicative/near-duplicate? [TODO]
  - Keep? [TODO]
- Reviewer note: TODO

## Sample 44
- Split: train
- Source: hf_diabetes_qa
- Topic: complications
- Instruction: Explain the link between diabetes and oral health, and how dental checkups can mitigate the risks.
- Output: Diabetes can impair the body's immune system, making individuals more prone to gum disease and other oral health problems. Regular dental checkups help detect and treat these issues early, preventing further complications and promoting overall health.
- Checklist:
  - Readable and simple? [TODO]
  - Diabetes-centered? [TODO]
  - Tone consistent with ClaraCare? [TODO]
  - Unsafe advice or dosage? [TODO]
  - Duplicative/near-duplicate? [TODO]
  - Keep? [TODO]
- Reviewer note: TODO

## Sample 45
- Split: eval
- Source: synthetic
- Topic: what time of day is best to check blood sugar
- Instruction: What time of day is best to check my blood sugar?
- Output: It is good to check blood sugar in the morning before breakfast. This tells you your levels after fasting all night. You can also check after meals to see how food affects your sugar. Always talk to your doctor about the best times for you.
- Checklist:
  - Readable and simple? [TODO]
  - Diabetes-centered? [TODO]
  - Tone consistent with ClaraCare? [TODO]
  - Unsafe advice or dosage? [TODO]
  - Duplicative/near-duplicate? [TODO]
  - Keep? [TODO]
- Reviewer note: TODO

## Sample 46
- Split: train
- Source: hf_diabetes_qa
- Topic: blood_sugar_monitoring
- Instruction: What are some essential tips for traveling with diabetes?
- Output: Important travel tips include getting necessary vaccinations, carrying diabetes medications and supplies, packing snacks for emergencies, checking blood glucose levels regularly, limiting alcohol intake, and carrying medical identification.
- Checklist:
  - Readable and simple? [TODO]
  - Diabetes-centered? [TODO]
  - Tone consistent with ClaraCare? [TODO]
  - Unsafe advice or dosage? [TODO]
  - Duplicative/near-duplicate? [TODO]
  - Keep? [TODO]
- Reviewer note: TODO

## Sample 47
- Split: train
- Source: hf_diabetes_qa
- Topic: insulin
- Instruction: Besides insulated bags, what other precautions can individuals with diabetes take to prevent their insulin from being exposed to direct sunlight during travel?
- Output: In addition to insulated bags, individuals with diabetes should avoid placing insulin in direct sunlight, as heat can degrade its effectiveness. Storing insulin in a cooler bag or keeping it in a shaded area of a backpack can help protect it from the sun's rays.
- Checklist:
  - Readable and simple? [TODO]
  - Diabetes-centered? [TODO]
  - Tone consistent with ClaraCare? [TODO]
  - Unsafe advice or dosage? [TODO]
  - Duplicative/near-duplicate? [TODO]
  - Keep? [TODO]
- Reviewer note: TODO

## Sample 48
- Split: train
- Source: hf_diabetes_qa
- Topic: emotional_support
- Instruction: Besides relaxation techniques, are there other ways individuals with diabetes can mitigate the impact of stress on their condition?
- Output: In addition to relaxation techniques, individuals with diabetes can benefit from seeking support from loved ones, joining support groups, or consulting mental health professionals to develop coping strategies for stress management.
- Checklist:
  - Readable and simple? [TODO]
  - Diabetes-centered? [TODO]
  - Tone consistent with ClaraCare? [TODO]
  - Unsafe advice or dosage? [TODO]
  - Duplicative/near-duplicate? [TODO]
  - Keep? [TODO]
- Reviewer note: TODO

## Sample 49
- Split: eval
- Source: synthetic
- Topic: how to manage diabetes during a religious fast
- Instruction: How can I manage my diabetes while fasting for my religion?
- Output: Managing diabetes during a fast is important. Eat small, healthy meals before and after fasting. Choose foods that are high in fiber. Drink plenty of water. Monitor your blood sugar levels. Talk to your doctor for specific advice. Your health is important.
- Checklist:
  - Readable and simple? [TODO]
  - Diabetes-centered? [TODO]
  - Tone consistent with ClaraCare? [TODO]
  - Unsafe advice or dosage? [TODO]
  - Duplicative/near-duplicate? [TODO]
  - Keep? [TODO]
- Reviewer note: TODO

## Sample 50
- Split: train
- Source: hf_diabetes_qa
- Topic: blood_sugar_monitoring
- Instruction: What factors influence an individual's A1C target?
- Output: A1C targets are personalized based on factors such as the duration of diabetes, the presence of other health conditions, and individual health goals. Your healthcare provider will determine an appropriate A1C target for you.
- Checklist:
  - Readable and simple? [TODO]
  - Diabetes-centered? [TODO]
  - Tone consistent with ClaraCare? [TODO]
  - Unsafe advice or dosage? [TODO]
  - Duplicative/near-duplicate? [TODO]
  - Keep? [TODO]
- Reviewer note: TODO
