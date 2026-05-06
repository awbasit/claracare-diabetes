# Audit 50 Samples

Manual review checklist for dataset quality before SFT.

## Audit Allocation
- HF samples: 30
- Current real samples: 20
- Synthetic samples: 0 (intentionally excluded)
- Total samples: 50

## Sample 1
- Sample ID: 1
- Source: hf_diabetes_qa
- Topic: blood_sugar_monitoring
- Instruction: Can you explain how an individual's health goals might impact their A1C target?
- Output: An individual's health goals play a significant role in setting their A1C target. For instance, someone aiming to prevent complications might have a stricter target than someone focused on managing their diabetes without significant lifestyle changes.
- Checklist:
  - Diabetes-centered? [TODO]
  - Patient-facing? [TODO]
  - Simple language? [TODO]
  - Unsafe dosage advice? [TODO]
  - Too much jargon? [TODO]
  - Keep? [TODO]
- Reviewer note: TODO

## Sample 2
- Sample ID: 2
- Source: hf_diabetes_qa
- Topic: emergencies
- Instruction: What is the primary benefit of a medical identification tag for individuals with diabetes?
- Output: Medical identification tags alert emergency responders and medical professionals to a person's diabetes, allowing them to provide appropriate and timely care, especially when the individual is unable to communicate their condition.
- Checklist:
  - Diabetes-centered? [TODO]
  - Patient-facing? [TODO]
  - Simple language? [TODO]
  - Unsafe dosage advice? [TODO]
  - Too much jargon? [TODO]
  - Keep? [TODO]
- Reviewer note: TODO

## Sample 3
- Sample ID: 3
- Source: current_real_cleaned
- Topic: TODO
- Instruction: Is taking primolut safe while trying to conceive?

Hi, I am a 24 year old who has recently been diagnosed with pCOS, the doctors put me on Triquilar for 3 moths but the problem did not resolve now they are asking me to use primolut for 3 months, is it safe since Im trying to conceive. I am 153cm and weight 81.5kg and I dont have any medical history.
- Output: Hi , How are you doing ? PCOD ( Polycystic ovaries),This is a congenital condition, I mean it is a genetically programmed condition, you get it from your parents. When you suddenly put on weight, this cholesterol is converted into estrogen hormone ( if I may simulate- haven't you seen obese men developing breast & in young obese girls, who develop periods at younger age - they all have high levels of Estrogen hormone / female hormone) In your body too when fat, which is a store for tomorrow,is more than normal, this is converted to hormone which tips the balance between FSH (from brain ) & the ovarian hormone. FSH( Follicle Stimulating Hormone ) as name suggests stimulates follicle from ovary, but once the follicle is big enough to ovulate, the FSH is suppressed by the same estrogen hormone from ovary. But when the same estrogen hormone is coming from fat, brain is confused & follicle growth stops early at a smaller follicle size & will not rupture, next scan you will see all these follicles as POLY CYSTIC OVARIES.!!! this is usually associated with Obesity, irregular cycles, no periods for few months & later heavy periods with clots & fleshy masses, or spotting on & off , Thyroid abnormality & prolactin problem indirectly.You develop that extra-pad of fat around the mid-segment of body, especially waist, thighs & breast, no fat beyond elbow & knees. Excessive body hair growth, hair fall , dark shade over lower half of face, acne , oily face skin, black skin over back of neck, inner thighs & under surface of breast. May have a family history of Diabetes, especially father or his family.This will not allow ovulation to occur at time & so you cannot get pregnant, till treated. It also increases your chances of early pregnancy abortions. But this has a solution.Your weight has to be Weight(in Kgs)= Height (in cms)-100Your expected weight is 53-58 kgs.Once you reduce weight to normal range, you won't need any medicine to get periods or to get pregnant & pregnancy will be healthy. To reduce weight -NO FASTING, No junk food/ fast foods/ red meat, reduce snacks in between mealsHave low calories food, high proteinsRegular exercise ( especially for the waist & hip area), aerobics , yoga, brisk walking( swing your hands well)   ,try to reduce 2-4 kgs / month. Don't hurry on weight reduction, it will be difficult to maintain. As soon as you reduce at least 5 kgs , you will see changes.When you take Primolut-N only your periods get altered , does not do any good or ba
- Checklist:
  - Diabetes-centered? [TODO]
  - Patient-facing? [TODO]
  - Simple language? [TODO]
  - Unsafe dosage advice? [TODO]
  - Too much jargon? [TODO]
  - Keep? [TODO]
- Reviewer note: TODO

## Sample 4
- Sample ID: 4
- Source: hf_diabetes_qa
- Topic: blood_sugar_monitoring
- Instruction: Can you explain the autoimmune process involved in the development of type 1 diabetes?
- Output: Type 1 diabetes is an autoimmune disease where the body's immune system mistakenly attacks and destroys the insulin-producing cells (beta cells) in the pancreas. This leads to a deficiency in insulin production, which is essential for regulating blood sugar levels.
- Checklist:
  - Diabetes-centered? [TODO]
  - Patient-facing? [TODO]
  - Simple language? [TODO]
  - Unsafe dosage advice? [TODO]
  - Too much jargon? [TODO]
  - Keep? [TODO]
- Reviewer note: TODO

## Sample 5
- Sample ID: 5
- Source: hf_diabetes_qa
- Topic: blood_sugar_monitoring
- Instruction: What happens to the body's cells when insulin resistance occurs?
- Output: In insulin resistance, fat, muscle, and liver cells become less responsive to insulin. This means they are unable to effectively absorb glucose from the bloodstream for energy, leading to a buildup of glucose in the blood.
- Checklist:
  - Diabetes-centered? [TODO]
  - Patient-facing? [TODO]
  - Simple language? [TODO]
  - Unsafe dosage advice? [TODO]
  - Too much jargon? [TODO]
  - Keep? [TODO]
- Reviewer note: TODO

## Sample 6
- Sample ID: 6
- Source: hf_diabetes_qa
- Topic: blood_sugar_monitoring
- Instruction: What are the benefits of monitoring blood glucose levels for individuals with diabetes?
- Output: Regular blood glucose monitoring helps prevent complications associated with uncontrolled diabetes, such as nerve damage, eye problems, and kidney disease. It also empowers individuals to actively participate in their own health management.
- Checklist:
  - Diabetes-centered? [TODO]
  - Patient-facing? [TODO]
  - Simple language? [TODO]
  - Unsafe dosage advice? [TODO]
  - Too much jargon? [TODO]
  - Keep? [TODO]
- Reviewer note: TODO

## Sample 7
- Sample ID: 7
- Source: hf_diabetes_qa
- Topic: blood_sugar_monitoring
- Instruction: What are the potential benefits of continuous glucose monitoring for individuals with diabetes?
- Output: Continuous glucose monitoring provides real-time blood glucose readings, allowing for proactive adjustments to food intake, physical activity, or medication, resulting in tighter blood glucose control and a reduced risk of hypoglycemia or hyperglycemia.
- Checklist:
  - Diabetes-centered? [TODO]
  - Patient-facing? [TODO]
  - Simple language? [TODO]
  - Unsafe dosage advice? [TODO]
  - Too much jargon? [TODO]
  - Keep? [TODO]
- Reviewer note: TODO

## Sample 8
- Sample ID: 8
- Source: hf_diabetes_qa
- Topic: diet_lifestyle
- Instruction: How can individuals with diabetes connect with a qualified nutrition professional in their neighborhood?
- Output: The Academy of Nutrition and Dietetics' website (www.eatright.org) provides a directory where you can find registered dietitians in your local area.
- Checklist:
  - Diabetes-centered? [TODO]
  - Patient-facing? [TODO]
  - Simple language? [TODO]
  - Unsafe dosage advice? [TODO]
  - Too much jargon? [TODO]
  - Keep? [TODO]
- Reviewer note: TODO

## Sample 9
- Sample ID: 9
- Source: current_real_cleaned
- Topic: TODO
- Instruction: Suggest treatment for very high BP

hi.....I'm a 43 year old male thats 290 lbs and I just had my bp checked and it was 186/83...... I've been working on my weight and hitting the gym for the last 6 weeks. I've lost 27 lbs and getting arms like a  body builder.....I just wanted to get your thought on the BP?
- Output: Hello!Thank you for asking on HCM!Your blood pressure values are above the normal ranges. This could be related to overweight or straining physical activity. Nevertheless, I would recommend consulting with your attending physician for a physical exam and some tests to investigate for other possible secondary causes of high blood pressure: - a resting ECG- a chest X ray study- some blood lab tests (complete blood count, blood lipid profile, fasting glucose, kidney and liver function tests, blood electrolytes, PCR, sedimentation rate)- an urine analysisIf all the above tests result normal, you should discuss with your doctor on the possibility of starting anti-hypertensive therapy, in order to have a better control of high blood pressure. I would also recommend some tips to help you maintain a normal blood pressure: - diet modifications (reduce salt and caffeine intake, avoid energetic drinks or pre-workout supplements)- avoid straining physical activity- try to reduce your weight (a dietitian may help you in this regard). Hope to have been helpful!Kind regards, Dr. Iliri
- Checklist:
  - Diabetes-centered? [TODO]
  - Patient-facing? [TODO]
  - Simple language? [TODO]
  - Unsafe dosage advice? [TODO]
  - Too much jargon? [TODO]
  - Keep? [TODO]
- Reviewer note: TODO

## Sample 10
- Sample ID: 10
- Source: current_real_cleaned
- Topic: TODO
- Instruction: What cause severe pain from calf to butt during night?

Was sleeping and in middle of the night I heard a pop sound in my right calf and since then I have severe pain from calf to butt. It really gets bad at night. This is now the fourth day and not better. I have se ere arthritis, diabetesm, and fibromyalgia. Arthritis is RAThank u
- Output: Hai.unfortunately u hav many medical problems which can cause pain.pls keep ur limbs elevated wenever u rest.u can also use a crepe bandage please try  with tab pregablin m a combination of pregablin and methylcobal.pls check out for deep vein thrombosis with doppler study of the affected limb
- Checklist:
  - Diabetes-centered? [TODO]
  - Patient-facing? [TODO]
  - Simple language? [TODO]
  - Unsafe dosage advice? [TODO]
  - Too much jargon? [TODO]
  - Keep? [TODO]
- Reviewer note: TODO

## Sample 11
- Sample ID: 11
- Source: current_real_cleaned
- Topic: TODO
- Instruction: How to reduce liver enzymes in body?

My husband had a routine check up and his liver enzyme came back at 490. Tested for Hepititus and it s negative. He went back in for a re test and now it s 166. This was three days later, now they want a sonogram of his liver. What can he do to lower this event more? He doesn t drink but occasionally and stopped that couple months ago. Eats healthy and recently started working out at a gym.
- Output: Good morning I am sorry to hear about his ill health Elevated alt indicates liver problem and it can be due to drugs or fatty liver So I would suggest to identify any such drug if any and stop it.  Fatty liver is commonly associated with obesity and diabetes mellitus which needs to be treated for reduction in liver enzymesHope this would answer your question Wish him speedy recovery
- Checklist:
  - Diabetes-centered? [TODO]
  - Patient-facing? [TODO]
  - Simple language? [TODO]
  - Unsafe dosage advice? [TODO]
  - Too much jargon? [TODO]
  - Keep? [TODO]
- Reviewer note: TODO

## Sample 12
- Sample ID: 12
- Source: hf_diabetes_qa
- Topic: blood_sugar_monitoring
- Instruction: Question: What are the four key daily actions that individuals with diabetes should take to ensure their blood glucose levels remain within a healthy range?
- Output: The four essential daily actions include: 1) making healthy food choices, 2) engaging in physical activity, 3) taking medications as prescribed, and 4) regularly monitoring blood glucose levels.
- Checklist:
  - Diabetes-centered? [TODO]
  - Patient-facing? [TODO]
  - Simple language? [TODO]
  - Unsafe dosage advice? [TODO]
  - Too much jargon? [TODO]
  - Keep? [TODO]
- Reviewer note: TODO

## Sample 13
- Sample ID: 13
- Source: hf_diabetes_qa
- Topic: blood_sugar_monitoring
- Instruction: What is glucagon, and how is it used in the management of severe hypoglycemia?
- Output: Glucagon is a medication that rapidly raises blood glucose levels. It is administered as an injection to treat severe hypoglycemia, typically by a trained family member, friend, or coworker.
- Checklist:
  - Diabetes-centered? [TODO]
  - Patient-facing? [TODO]
  - Simple language? [TODO]
  - Unsafe dosage advice? [TODO]
  - Too much jargon? [TODO]
  - Keep? [TODO]
- Reviewer note: TODO

## Sample 14
- Sample ID: 14
- Source: hf_diabetes_qa
- Topic: insulin
- Instruction: Can X-ray machines have a negative impact on insulin pumps?
- Output: Yes, X-ray machines can potentially damage insulin pumps. It is advisable to request a manual inspection from airport security to avoid any potential harm to the device.
- Checklist:
  - Diabetes-centered? [TODO]
  - Patient-facing? [TODO]
  - Simple language? [TODO]
  - Unsafe dosage advice? [TODO]
  - Too much jargon? [TODO]
  - Keep? [TODO]
- Reviewer note: TODO

## Sample 15
- Sample ID: 15
- Source: hf_diabetes_qa
- Topic: medication
- Instruction: Besides medications for diabetes itself, what other types of drugs might a doctor prescribe for diabetes-related complications?
- Output: In addition to diabetes medications, doctors often prescribe medications to address related health issues. These can include aspirin for heart health, cholesterol-lowering drugs to manage high cholesterol, and medications for high blood pressure.
- Checklist:
  - Diabetes-centered? [TODO]
  - Patient-facing? [TODO]
  - Simple language? [TODO]
  - Unsafe dosage advice? [TODO]
  - Too much jargon? [TODO]
  - Keep? [TODO]
- Reviewer note: TODO

## Sample 16
- Sample ID: 16
- Source: hf_diabetes_qa
- Topic: blood_sugar_monitoring
- Instruction: How can stress affect blood glucose levels in individuals with diabetes?
- Output: Stress hormones can raise blood glucose levels, making stress management techniques important for diabetes control.
- Checklist:
  - Diabetes-centered? [TODO]
  - Patient-facing? [TODO]
  - Simple language? [TODO]
  - Unsafe dosage advice? [TODO]
  - Too much jargon? [TODO]
  - Keep? [TODO]
- Reviewer note: TODO

## Sample 17
- Sample ID: 17
- Source: current_real_cleaned
- Topic: TODO
- Instruction: How can high blood pressure with dizziness be treated?

My husband  (50 years old) has high blood pressure, hes currently taking ramipril, doxisosin and amilodipine, (he stopped taking simvastitin as it was making his knee joints hurt) he drinks alcohol on the weekend only.He is about 14 stone 7. He has improved his diet, but his bp still hasnt come down. He is also getting dizzy spells and sometimes feels weak and cant move arms(this improves when he has food). what else can he do? Also is spicy food good or bad for his condition?
- Output: Hello!Welcome on HCM!I carefully passed through your question and would explain that it important performing some tests to investigate for other secondary causes of high blood pressure: - a chest X ray study- thyroid hormone levels for thyroid dysfunction- complete blood count for anemia- liver and kidney function tests- fasting glucose and HbA1C for diabetes- blood electrolytes for possible imbalance- cortisol and aldosterone plasma levels for possible adrenal gland dysfunction. If all the above tests result normal, I would recommend discussing with his doctor on the possibility of making some changes to his actual therapy (increase the doses of add a new antihypertensive drug), in order to have a better control of his blood pressure values. Regarding spicy food, I would not recommend them. I would also advice reduce salt and caffeine intake. A lot of physical activity (aerobics, swimming, etc.) can be helpful. Hope to have been helpful!Wishing all the best, Dr. Iliri
- Checklist:
  - Diabetes-centered? [TODO]
  - Patient-facing? [TODO]
  - Simple language? [TODO]
  - Unsafe dosage advice? [TODO]
  - Too much jargon? [TODO]
  - Keep? [TODO]
- Reviewer note: TODO

## Sample 18
- Sample ID: 18
- Source: hf_diabetes_qa
- Topic: diabetes_basics
- Instruction: What are the key benefits of engaging in physical activity for individuals with insulin resistance?
- Output: For individuals with insulin resistance, physical activity is crucial as it significantly improves insulin sensitivity, allowing their bodies to utilize glucose more effectively. This leads to better blood sugar control and a reduced risk of developing type 2 diabetes.
- Checklist:
  - Diabetes-centered? [TODO]
  - Patient-facing? [TODO]
  - Simple language? [TODO]
  - Unsafe dosage advice? [TODO]
  - Too much jargon? [TODO]
  - Keep? [TODO]
- Reviewer note: TODO

## Sample 19
- Sample ID: 19
- Source: hf_diabetes_qa
- Topic: emotional_support
- Instruction: How can individuals with diabetes utilize the internet to enhance their self-management strategies?
- Output: The internet provides a vast array of tools and resources for individuals with diabetes. They can utilize diabetes management apps for tracking their condition, connect with others in online communities for support, and access educational websites from reputable organizations like the American Diabetes Association and the NIDDK for reliable information.
- Checklist:
  - Diabetes-centered? [TODO]
  - Patient-facing? [TODO]
  - Simple language? [TODO]
  - Unsafe dosage advice? [TODO]
  - Too much jargon? [TODO]
  - Keep? [TODO]
- Reviewer note: TODO

## Sample 20
- Sample ID: 20
- Source: current_real_cleaned
- Topic: TODO
- Instruction: What causes pain in the chest and abdomen?

Hye , I am 51 years  old. Female. I have dibatec problem(4year) & found cercinoma in my taunge 3years ago & successufully operated, Uterus & Gall Bladder is operated. Presently i feel tired, My hand & wrist pain.Some time I have pain in my chest, abdominal pain & this pain will transfromed to back side.My weight little bit lose. My Pressure BP is low 90/60. Last Fasting Blood Glucose 6.7 mml/L.HBA1C is 7.9%A1C Corr. Urine Suger Nill, Creatinine 0.8. My TG is 396 mg/dl & my ECG reports : Poor progression of R wave V2-V3.
- Output: 1.    Spasms or narrowing of the esophagus (the tube that carries food from the mouth to the stomach)2.    Gallstones cause pain that gets worse after a meal (most often a fatty meal). Heartburn or gastroesophageal reflux (GERD)3.   Stomach ulcer or gastritis: Burning pain occurs if your stomach is empty and feels better when you eat food
- Checklist:
  - Diabetes-centered? [TODO]
  - Patient-facing? [TODO]
  - Simple language? [TODO]
  - Unsafe dosage advice? [TODO]
  - Too much jargon? [TODO]
  - Keep? [TODO]
- Reviewer note: TODO

## Sample 21
- Sample ID: 21
- Source: hf_diabetes_qa
- Topic: emotional_support
- Instruction: What are some potential benefits of being open about emotional difficulties related to diabetes with my healthcare provider?
- Output: Open communication about emotional challenges related to diabetes enables your healthcare provider to offer appropriate support, such as counseling or stress management techniques. These interventions can help you cope with the emotional aspects of diabetes and improve overall well-being.
- Checklist:
  - Diabetes-centered? [TODO]
  - Patient-facing? [TODO]
  - Simple language? [TODO]
  - Unsafe dosage advice? [TODO]
  - Too much jargon? [TODO]
  - Keep? [TODO]
- Reviewer note: TODO

## Sample 22
- Sample ID: 22
- Source: current_real_cleaned
- Topic: TODO
- Instruction: Which are the alternatives apart from IVF to get pregnant?

I have been diagnosed as being infertile (pcos, low progesterone and severe scarring as a result of pid). I visited a fertility clinic where i did an amh test (the results were good), I been told the only way to get pregnant is by ivf; are there any other fertility treatments that may work for me?
- Output: Hi , With these 3 reasons you don't need to take up IVF as first resort.1. PCO will have poor progestrone production because the eggs don't come out of ovary in PCO. - Best solution is controlled diet & regular exercise. No fasting. Avoid high cal diet. Confirm you Thyroid profile , Blood sugar & Serum Prolactin are normal.2. PID is infection which need a good antibiotic cover for husband & wife, to be started by Gynecologist.Hope other factors for infertility have been ruled out.Once PID is treated, PCO have a high chance for pregnancy with Ovulation inducing drugs +/-  hormonal support. Good AMH means you have lot of eggs.All the bestDr.Balakrishnan
- Checklist:
  - Diabetes-centered? [TODO]
  - Patient-facing? [TODO]
  - Simple language? [TODO]
  - Unsafe dosage advice? [TODO]
  - Too much jargon? [TODO]
  - Keep? [TODO]
- Reviewer note: TODO

## Sample 23
- Sample ID: 23
- Source: hf_diabetes_qa
- Topic: blood_sugar_monitoring
- Instruction: What kind of foods are recommended for treating low blood sugar, and why are these specific types of foods effective?
- Output: Fast-acting carbohydrate sources like glucose tablets, glucose gel, fruit juice, regular soft drink, milk, hard candy, or sugar are recommended for treating low blood sugar. These foods are effective because they are quickly absorbed into the bloodstream, raising blood glucose levels rapidly.
- Checklist:
  - Diabetes-centered? [TODO]
  - Patient-facing? [TODO]
  - Simple language? [TODO]
  - Unsafe dosage advice? [TODO]
  - Too much jargon? [TODO]
  - Keep? [TODO]
- Reviewer note: TODO

## Sample 24
- Sample ID: 24
- Source: hf_diabetes_qa
- Topic: other_diabetes
- Instruction: How can individuals with diabetes participate in collaborative decision-making with their healthcare providers?
- Output: Individuals with diabetes can participate in shared decision-making by openly discussing their preferences, asking questions about treatment options, and expressing their concerns about potential risks and benefits. This collaborative approach helps ensure their needs and preferences are considered in their care plan.
- Checklist:
  - Diabetes-centered? [TODO]
  - Patient-facing? [TODO]
  - Simple language? [TODO]
  - Unsafe dosage advice? [TODO]
  - Too much jargon? [TODO]
  - Keep? [TODO]
- Reviewer note: TODO

## Sample 25
- Sample ID: 25
- Source: current_real_cleaned
- Topic: TODO
- Instruction: How can diabetes ketoacidosis be diagnosed?

Hi...I am looking for info on diabetes and ketoacidosis.  My company thought I was drinking one night, and I had not, but there was a smell that I can't explain. I did some research and plan on seeing my primary, but i want to know how to ask the right questions. Thanks
- Output: Welcome to HealthcareMagic .diabetic ketoacidosis is diagnosed by blood tests having raised ketones and raised sugar and normal or low potassium and bicarbonate .basically it is decompensated diabetes ..acidotic smell will be there .if you have any further query then you can come back to HealthcareMagic i will definitely help you and guide you appropriately .with regards dr varinder joshi
- Checklist:
  - Diabetes-centered? [TODO]
  - Patient-facing? [TODO]
  - Simple language? [TODO]
  - Unsafe dosage advice? [TODO]
  - Too much jargon? [TODO]
  - Keep? [TODO]
- Reviewer note: TODO

## Sample 26
- Sample ID: 26
- Source: hf_diabetes_qa
- Topic: blood_sugar_monitoring
- Instruction: What is the specific target of the immune system in the development of type 1 diabetes?
- Output: The immune system in type 1 diabetes targets the beta cells within the pancreas, which are responsible for producing insulin. This autoimmune attack disrupts the body's ability to regulate blood sugar levels.
- Checklist:
  - Diabetes-centered? [TODO]
  - Patient-facing? [TODO]
  - Simple language? [TODO]
  - Unsafe dosage advice? [TODO]
  - Too much jargon? [TODO]
  - Keep? [TODO]
- Reviewer note: TODO

## Sample 27
- Sample ID: 27
- Source: current_real_cleaned
- Topic: TODO
- Instruction: How to treat in prostatomegaly geade2?

Dear Dr.My father is 66 yrs old sufering from prostatomegay geade2, size-3.9x4.1x4.5; weight 38.7 gm capsule intact & other organs like liver,kidny, urine bladder etc. are normal; plz advise me that is it treated with medicine or laproscopy.....plz advise me
- Output: HelloYour father's findings suggests moderately enlarged prostate.He may need proper clinical examination and investigations.Investigation include routine hemogram,random blood sugar,urine RE/ME.He may need PSA(prostate specific antigen)after evaluation.Enlarged prostate is managed by both conservative and by surgery.Since he has moderate enlargement he may only need medicines and follow up.He may need medicines like 5-alpha reductase inhibitors(finasteride) or alpha blockers. It need evaluation by a urologist.Get well soon.Take CareDr.Indu Bhushan
- Checklist:
  - Diabetes-centered? [TODO]
  - Patient-facing? [TODO]
  - Simple language? [TODO]
  - Unsafe dosage advice? [TODO]
  - Too much jargon? [TODO]
  - Keep? [TODO]
- Reviewer note: TODO

## Sample 28
- Sample ID: 28
- Source: hf_diabetes_qa
- Topic: blood_sugar_monitoring
- Instruction: What kind of information should individuals with diabetes prioritize discussing with their healthcare team during each visit, based on the "Things to Discuss with Your Health Care Team at Each Visit" chart?
- Output: The chart encourages individuals with diabetes to discuss key aspects of their diabetes management, such as blood sugar levels, medications, lifestyle changes, and any concerns or questions they may have, ensuring a holistic and well-rounded approach to their care.
- Checklist:
  - Diabetes-centered? [TODO]
  - Patient-facing? [TODO]
  - Simple language? [TODO]
  - Unsafe dosage advice? [TODO]
  - Too much jargon? [TODO]
  - Keep? [TODO]
- Reviewer note: TODO

## Sample 29
- Sample ID: 29
- Source: current_real_cleaned
- Topic: TODO
- Instruction: What could cause muscle jerking in arms & legs in elderly males?

Hello I have started having muscle jerking in my arms & legs. I am 77 years old. A little over weight. I have neuromas in both feet & neuropathy in my feet & legs. I don t know if this has anything to do with the jerking. I am also a diabetic. Healthy & strong until the last 10 years. I have had 3 surgeries on my feet for the neuromas but keep coming back. I have a difficult time walking & standing because of the pain caused by these things. Any suggestion you could make would be welcomed. Mary Bryan
- Output: Hi mary bryanHope this message finds you in good health.I have gone through your complaints and understand your concern.I guess the neuromas are the root cause of such jerking because they are attached to muscle. There is no specific treatment that will cure it permanently.U need to keep  watch on its progress,stay healthy.Nothing to worry about.     I hope your question has been answered.If you have any follow-up queries,feel free to consult me anytime.Thanks,Take care,God bless.
- Checklist:
  - Diabetes-centered? [TODO]
  - Patient-facing? [TODO]
  - Simple language? [TODO]
  - Unsafe dosage advice? [TODO]
  - Too much jargon? [TODO]
  - Keep? [TODO]
- Reviewer note: TODO

## Sample 30
- Sample ID: 30
- Source: current_real_cleaned
- Topic: TODO
- Instruction: What causes head ache and light headed?

I am adult on set diabetic well controlled. I have hypertension. Monday My heart started beating really fast. Pulse 97, BP 197/103.  Today I woke up with head ache and feeling light headed. Went to work and had another attack of head pressure and hands were trembling.
- Output: Hello,Thanks for writing to health care magic,This is quite a high blood pressure reading and with this reading even once you will need serious care and medication along with life style changes.I would suggest you to take your blood pressure at home twice a day and then visit your cardiologist with the chart of blood pressure to get treatment started according to your BP readings.Till then its important for you to lower your salt intake, dont take caffeine in any form. Keep a healthy weight . And keep monitoring your bp to keep it under 150/80Best regards.Dr.Ahmad
- Checklist:
  - Diabetes-centered? [TODO]
  - Patient-facing? [TODO]
  - Simple language? [TODO]
  - Unsafe dosage advice? [TODO]
  - Too much jargon? [TODO]
  - Keep? [TODO]
- Reviewer note: TODO

## Sample 31
- Sample ID: 31
- Source: hf_diabetes_qa
- Topic: complications
- Instruction: What is the role of aspirin in diabetes management, and why is it often recommended?
- Output: Low-dose aspirin is often recommended for individuals with diabetes to reduce the risk of heart disease, as they are at increased cardiovascular risk.
- Checklist:
  - Diabetes-centered? [TODO]
  - Patient-facing? [TODO]
  - Simple language? [TODO]
  - Unsafe dosage advice? [TODO]
  - Too much jargon? [TODO]
  - Keep? [TODO]
- Reviewer note: TODO

## Sample 32
- Sample ID: 32
- Source: current_real_cleaned
- Topic: TODO
- Instruction: What is the treatment for ejaculation problems?

Good Morning... i have a question... i am planning for a family what i have realized that while having intercource i donot eject semen everytime. it ha shappened to me couple of times.. need to know whether i should consult a doctor or is it normal???
- Output: Hello, In some men this problem is seen. try changing position. Spend time in foreplay and continue pushing (remaining still inside the vagina may cause lack of stimulation and ejaculation problem). Try Kegel exercise. If still the problem persists, please consult doctor to find out the cause. The problem may lie in the prostate gland, blood sugar or in the spine or nerve. In few men, the problem can persist despite all treatment. In that case, you can try self-insemination (collecting semen at home and inserting it inside the vagina) It works. Some of my patients conceived after this self-insemination. Hope I have answered your query. Let me know if I can assist you further. Take care Regards, Dr. Sujoy Dasgupta
- Checklist:
  - Diabetes-centered? [TODO]
  - Patient-facing? [TODO]
  - Simple language? [TODO]
  - Unsafe dosage advice? [TODO]
  - Too much jargon? [TODO]
  - Keep? [TODO]
- Reviewer note: TODO

## Sample 33
- Sample ID: 33
- Source: current_real_cleaned
- Topic: TODO
- Instruction: Is typhoid a common cause for left-sided abdominal pain ?

I have pain in my left side and back since yesterday. I have been on medication for typhoid upto last week - 31st july. I am a diabetic and am on medication for the same,as also for hypertension .
- Output: Hi,Vinny, Thanks for query, If temperature is alright then nothing to worry, Pain may be due to as in typhoid infection and soreness in the intestine causing pain in abdomen. Due to constipation which is common in typhoid may also cause pain. Take liquid diet and plenty of water. Ok and bye.
- Checklist:
  - Diabetes-centered? [TODO]
  - Patient-facing? [TODO]
  - Simple language? [TODO]
  - Unsafe dosage advice? [TODO]
  - Too much jargon? [TODO]
  - Keep? [TODO]
- Reviewer note: TODO

## Sample 34
- Sample ID: 34
- Source: hf_diabetes_qa
- Topic: emotional_support
- Instruction: Can stretching be beneficial for individuals with diabetes? If so, how?
- Output: Yes, stretching is beneficial for individuals with diabetes. It promotes flexibility, improves blood flow, and helps reduce stress, all of which contribute to overall well-being and diabetes management.
- Checklist:
  - Diabetes-centered? [TODO]
  - Patient-facing? [TODO]
  - Simple language? [TODO]
  - Unsafe dosage advice? [TODO]
  - Too much jargon? [TODO]
  - Keep? [TODO]
- Reviewer note: TODO

## Sample 35
- Sample ID: 35
- Source: current_real_cleaned
- Topic: TODO
- Instruction: What causes pain in upper left stomach area just below ribs?

I have pain on my upper left stomach area, right below my ribs. If I am standing it really doesn t hurt but setting or leaning forward does. It also has a sensation like something there is knotting up and almost like it is moving. The pain isn t severe but it is pretty constant. I am 44 yr old female, over weight with high blood pressure. Thanks
- Output: Hi! Good afternoon. I am Dr Shareef answering your query.If I were your doctor, I would like to have a clinical examination of yours followed by an ultrasound of whole abdomen to see the status of all the intra abdominal organs or any other related lumps. Apart from this,  I would also go for some routine tests like a CBC, a blood sugar, serum amylase and lipase, and a LFT. A routine ECG would also be worth doing. I would also advise you to avoid any alcoholic beverages or smoking if you do. Further management would depend on the clinical findings, and investigation reports. Till then, you could go for a anti spasmodic and a proton pump inhibitor drug for a symptomatic relief. I hope this information would help you in discussing with your family physician/treating doctor in further management of your problem. Please do not hesitate to ask in case of any further doubts.Thanks for choosing health care magic to clear doubts on your health problems. I wish you an early recovery. Dr Shareef.
- Checklist:
  - Diabetes-centered? [TODO]
  - Patient-facing? [TODO]
  - Simple language? [TODO]
  - Unsafe dosage advice? [TODO]
  - Too much jargon? [TODO]
  - Keep? [TODO]
- Reviewer note: TODO

## Sample 36
- Sample ID: 36
- Source: hf_diabetes_qa
- Topic: blood_sugar_monitoring
- Instruction: How does continuous glucose monitoring differ from traditional blood glucose testing?
- Output: Continuous glucose monitoring provides real-time blood glucose readings throughout the day and night, offering a more detailed and comprehensive view of glucose fluctuations compared to intermittent finger-prick tests.
- Checklist:
  - Diabetes-centered? [TODO]
  - Patient-facing? [TODO]
  - Simple language? [TODO]
  - Unsafe dosage advice? [TODO]
  - Too much jargon? [TODO]
  - Keep? [TODO]
- Reviewer note: TODO

## Sample 37
- Sample ID: 37
- Source: hf_diabetes_qa
- Topic: blood_sugar_monitoring
- Instruction: Why is it not advisable to engage in physical activity right before bed for individuals taking insulin?
- Output: Physical activity close to bedtime can increase the risk of low blood glucose levels during sleep (nocturnal hypoglycemia) for those taking insulin, as insulin's effects can be prolonged.
- Checklist:
  - Diabetes-centered? [TODO]
  - Patient-facing? [TODO]
  - Simple language? [TODO]
  - Unsafe dosage advice? [TODO]
  - Too much jargon? [TODO]
  - Keep? [TODO]
- Reviewer note: TODO

## Sample 38
- Sample ID: 38
- Source: current_real_cleaned
- Topic: TODO
- Instruction: What is the treatment for cough , cold and fever?

HI, I m type II dm. currently on Metformin 500 (xr) & glicazide 60mg BID. came down with the flu associated with a bad cough and cold. my diabetologist prescribed augmentin 625 BID and bifilac BID for 5 days therapy to address the flu , this is after i took OTC flu meds for 14 days, since it was persistent he wrote the above. my question is will these meds affect by sugar levels, also since the first dose, I m getting weak and drowsy. please let me know should i continue the meds with my diabetic meds also I m on finofibrate 145mcg qd . thank you.
- Output: HiWelcome to Health care magic.I went through the history you have provided here. It seems from the history that you are having that you are a known diabetic on treatment with Metformin and Glicazide tablets.The treatment prescribed for fever, cough and cold by antibiotic in the form of Augmentin is in correct direction and these tablets will not affect the sugar levels. You need to continue the treatment as advised by your doctor along with the diabetic medicines.Hope this is helpful to you.Do write back to me for further questions.Thank you for writing to us.
- Checklist:
  - Diabetes-centered? [TODO]
  - Patient-facing? [TODO]
  - Simple language? [TODO]
  - Unsafe dosage advice? [TODO]
  - Too much jargon? [TODO]
  - Keep? [TODO]
- Reviewer note: TODO

## Sample 39
- Sample ID: 39
- Source: hf_diabetes_qa
- Topic: blood_sugar_monitoring
- Instruction: What are the potential consequences of stopping diabetes medications without consulting a doctor?
- Output: Abruptly stopping diabetes medications can lead to a rapid increase in blood glucose levels, potentially causing hyperglycemia and related complications. Always consult your doctor before making any changes to your medication regimen.
- Checklist:
  - Diabetes-centered? [TODO]
  - Patient-facing? [TODO]
  - Simple language? [TODO]
  - Unsafe dosage advice? [TODO]
  - Too much jargon? [TODO]
  - Keep? [TODO]
- Reviewer note: TODO

## Sample 40
- Sample ID: 40
- Source: current_real_cleaned
- Topic: TODO
- Instruction: What causes erection while sleeping with difficulty in ejaculation?

I am a 57 year old heterosexual male who had a burst vein in my right cortex affecting my left arm and leg, short term memory, and a few other things. My stroke was aprox. 5 weeks ago. I have been experincing erections in my sleep since the 3rd week, but seem unable to get a complete erection or ejaculate. Any hope getting all of this back? Any therapy for this?
- Output: Hi, It can be due to retrograde ejaculation, diabetes and prostate infection. rule out for prostate infection. Did you take any treatment for that burst of your vein? if you have any report of that treatment, you can upload it for further consultation? Hope I have answered your query. Let me know if I can assist you further. Regards, Dr. S. R. Raveendran, Sexologist
- Checklist:
  - Diabetes-centered? [TODO]
  - Patient-facing? [TODO]
  - Simple language? [TODO]
  - Unsafe dosage advice? [TODO]
  - Too much jargon? [TODO]
  - Keep? [TODO]
- Reviewer note: TODO

## Sample 41
- Sample ID: 41
- Source: current_real_cleaned
- Topic: TODO
- Instruction: What are the home remedies for treating tinea versicolor?

Hi doctor, i was diagnosed with tinea versicolor years ago. I was told that it does not go away completely but if i apply sulfur that would help. However, sulfur smells really bad and the tinea mostly appear in summer. i am wearing t-shirts to cover up and i always try to hid my body. Is there any home remedies i could use for the fungus instead of sulfur to avoid smelling?
- Output: Hi dear i read ur problem of Tinea versicolor since 1yr and not completely go away.First u dont tell about ur age because ur duration of disease is 1yr so some investigation is needed.1-blood sugar PP and fasting2-Thyroid profile3-GBP(general blood picture)Precaustions-AVOID SPICY AND PROCESSED  FOOD IN UR DIET.EVERYDAY BATHING SHOULD BE NECESSARY BECAUSE PROFUSE SWEATING SHOULD BE ONE OF THE PASIPITATING FACTOR.U CAN TAKE LEAVES OF NEEM  AND BOILED IT AND USED FOR BATH.TREATMENT-1-U CAN TAKE 2LEAVES OF NEEM AND DIP IN ONE GLASS WATER AT NIGHT AND DRINK IT AT EARLY MORNING.2-U CAN TAKE GANDAHK RASAYAN 125mg  Three times a day.3-TAKE SEPTILIN(HIMALAYA) TAB(2) THREE TIMES IN A DAY.4-U CAN TAKE HAEMOCLEEN SYRUP (2TSF) IN A DAY.5-USE NEEM SOAP DURING  BATHING.     THANKS FOR QUERY.
- Checklist:
  - Diabetes-centered? [TODO]
  - Patient-facing? [TODO]
  - Simple language? [TODO]
  - Unsafe dosage advice? [TODO]
  - Too much jargon? [TODO]
  - Keep? [TODO]
- Reviewer note: TODO

## Sample 42
- Sample ID: 42
- Source: hf_diabetes_qa
- Topic: emergencies
- Instruction: Besides medical supplies, what other important documents should be included in a diabetes disaster kit?
- Output: In addition to medical supplies, a diabetes disaster kit should include a copy of your medical information, such as your diabetes management plan, and emergency contact numbers.
- Checklist:
  - Diabetes-centered? [TODO]
  - Patient-facing? [TODO]
  - Simple language? [TODO]
  - Unsafe dosage advice? [TODO]
  - Too much jargon? [TODO]
  - Keep? [TODO]
- Reviewer note: TODO

## Sample 43
- Sample ID: 43
- Source: current_real_cleaned
- Topic: TODO
- Instruction: Can lower abdominal pain be a sign of urine infection?

I am having lower abdominal pain, right above the pubic bone, almost like cramping. When I urinate the pain seems to ease.  I am 42, 5"3" tall and weigh 205.  I am also diabetic.  Just trying to determine if this might be a sign of infection that I should follow up with my doctor.
- Output: HI.Since you are diabetic and have this problem, you should consult a Doctor for clinical examination investigations and treatment according to the findings. I would advise:Send samples before an antibiotic is started . Blood -complete blood picture.Urine- routine, microscopy, culture and sensitivity. Ultrasonography of abdomen. Start the roper treatment for diabetes and the infection. You will be fine.take an antibiotic course of 7 to 21 days.
- Checklist:
  - Diabetes-centered? [TODO]
  - Patient-facing? [TODO]
  - Simple language? [TODO]
  - Unsafe dosage advice? [TODO]
  - Too much jargon? [TODO]
  - Keep? [TODO]
- Reviewer note: TODO

## Sample 44
- Sample ID: 44
- Source: hf_diabetes_qa
- Topic: healthcare_visit
- Instruction: How do clinical trials contribute to the advancement of diabetes care?
- Output: Clinical trials play a vital role in improving diabetes care by testing new treatments, prevention strategies, and management approaches. They provide evidence-based data to inform healthcare decisions and ensure that patients receive the most effective and safe interventions.
- Checklist:
  - Diabetes-centered? [TODO]
  - Patient-facing? [TODO]
  - Simple language? [TODO]
  - Unsafe dosage advice? [TODO]
  - Too much jargon? [TODO]
  - Keep? [TODO]
- Reviewer note: TODO

## Sample 45
- Sample ID: 45
- Source: hf_diabetes_qa
- Topic: blood_sugar_monitoring
- Instruction: Besides managing blood sugar levels, what other health-related goals should individuals with diabetes strive for?
- Output: Along with blood sugar control, individuals with diabetes should aim for a healthy weight, regular physical activity, and a balanced diet to promote overall health and well-being.
- Checklist:
  - Diabetes-centered? [TODO]
  - Patient-facing? [TODO]
  - Simple language? [TODO]
  - Unsafe dosage advice? [TODO]
  - Too much jargon? [TODO]
  - Keep? [TODO]
- Reviewer note: TODO

## Sample 46
- Sample ID: 46
- Source: hf_diabetes_qa
- Topic: medication
- Instruction: Can you provide some examples of medications that are not directly for diabetes but are commonly prescribed for people with diabetes?
- Output: Yes, many individuals with diabetes also require medications for other health concerns linked to the condition. These can include aspirin to prevent heart problems, cholesterol-lowering medications to manage high cholesterol, and medications for high blood pressure.
- Checklist:
  - Diabetes-centered? [TODO]
  - Patient-facing? [TODO]
  - Simple language? [TODO]
  - Unsafe dosage advice? [TODO]
  - Too much jargon? [TODO]
  - Keep? [TODO]
- Reviewer note: TODO

## Sample 47
- Sample ID: 47
- Source: current_real_cleaned
- Topic: TODO
- Instruction: What causes sudden shortness of breath?

my mom was very short of breath for a couple days...her sugar went to 500 the ambulance came and gave her some breathing treatment in which she then became completely unresponsive. she got to the hospital and they were bagging her...she then vent tact and then bradycardia and then vfib. they said she was unconscious but could she know what was happeneing. her bnp was greater than 175,000 what does that mean?????please help me I have been struggling with this for 10 months
- Output: In diabetic patients when sugar level goes high in blood it causes liberation of ketone bodies this condition is known as diabetic ketoacidosis which causes sudden shortness of breath and increased respiratory rate with frooty odoured breath. Urine examination should be done for ketone bodies and  monitoring sugar levels along with antidiabetic drugs and a full cardiac assesment. It will be helpful.
- Checklist:
  - Diabetes-centered? [TODO]
  - Patient-facing? [TODO]
  - Simple language? [TODO]
  - Unsafe dosage advice? [TODO]
  - Too much jargon? [TODO]
  - Keep? [TODO]
- Reviewer note: TODO

## Sample 48
- Sample ID: 48
- Source: hf_diabetes_qa
- Topic: blood_sugar_monitoring
- Instruction: What is the purpose of checking blood glucose levels?
- Output: Checking blood glucose levels helps monitor diabetes control and provides insights into the effectiveness of your treatment plan.
- Checklist:
  - Diabetes-centered? [TODO]
  - Patient-facing? [TODO]
  - Simple language? [TODO]
  - Unsafe dosage advice? [TODO]
  - Too much jargon? [TODO]
  - Keep? [TODO]
- Reviewer note: TODO

## Sample 49
- Sample ID: 49
- Source: current_real_cleaned
- Topic: TODO
- Instruction: How can severe erectile dysfunction be treated?

Sir me last 10 years se regular masturbation kar raha hun I am Suffering from erectile dysfunction and testicle pain after masturbation I am 30 years old male, not married. My problem is that i am not able to sustain erection for long and i tend to ejaculate in 10 to 15 seconds only during masturbation. This problem is from the beginning. And after masturbation i feel little pain near testicles area like thighs, hips and all. Also i am feeling that erection is not so hard . I am worried about my to be married life . Please advice.
- Output: Hello welcome to the health care magic You are having over masturbation problem.. Usually it is safe practice but sometime when overpractising it can lead social anxiety,  chronic fatigue etc... For avoid over masturbation yoga,  meditation beneficial Try to avoid watching excess porn videos and magazines Make short term and long term goals and fulfill it For erectile dysfunction before marriage following problem should be ruled out for your case .... -Hypertension -Diabetes-high cholesterol-prostate problem if suspected -Smoking -medication history -cardiovascular problems etc.... According to cause found specific treatment given Take care Hope your concern solved Consult physician or psychiatrist  for examination and discuss all these with him
- Checklist:
  - Diabetes-centered? [TODO]
  - Patient-facing? [TODO]
  - Simple language? [TODO]
  - Unsafe dosage advice? [TODO]
  - Too much jargon? [TODO]
  - Keep? [TODO]
- Reviewer note: TODO

## Sample 50
- Sample ID: 50
- Source: hf_diabetes_qa
- Topic: insulin
- Instruction: Besides insulated bags, what other precautions can individuals with diabetes take to prevent their insulin from being exposed to direct sunlight during travel?
- Output: In addition to insulated bags, individuals with diabetes should avoid placing insulin in direct sunlight, as heat can degrade its effectiveness. Storing insulin in a cooler bag or keeping it in a shaded area of a backpack can help protect it from the sun's rays.
- Checklist:
  - Diabetes-centered? [TODO]
  - Patient-facing? [TODO]
  - Simple language? [TODO]
  - Unsafe dosage advice? [TODO]
  - Too much jargon? [TODO]
  - Keep? [TODO]
- Reviewer note: TODO
