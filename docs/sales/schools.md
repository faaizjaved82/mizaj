# Selling Career Compass to schools

**Who:** principal, vice principal, head of O/A-level or FSc section, careers counsellor. Private chains (Educators,
Allied, The City School, Beaconhouse, Roots, LGS), independent schools, colleges (FSc/ICS/I.Com), and academies.

**When:** Jan–Mar (stream choice after mock exams), Apr–May (before board exams end), Jul–Sep (result season, the
biggest window).

**Offer:** free pilot for 30 students → class pack PKR 300/student (min 50) → career day PKR 500/student with a
session by a partner counsellor (30% of the session fee to them).

## Email (draft, personalise the first line)

Subject: Free career pilot for {School}'s Grade {10/11} students

Assalam o Alaikum {Name},

{One specific line about the school: a recent result, a campus, a programme.}

Every year students pick Pre-Medical, Pre-Engineering, ICS or Commerce because a cousin did, and many regret it.
Mizaj Career Compass helps them choose with evidence: a 15-minute test on any phone, in English or Urdu, that gives
each student their interest code and personality type, matched to Pakistani streams, degrees and entry tests, plus a
page written for their parents. Your counsellor gets a class summary.

We'd like to run it free for 30 of your students this month. If it's useful, the full class costs PKR 300 per
student, far less than a single private counselling session.

Could I send you the pilot link, or visit for 15 minutes?

Shukriya,
{Owner name} · Mizaj · mizaj.pk/schools · {WhatsApp}

## WhatsApp follow-up (after 4 days)
Assalam o Alaikum {Name}, following up on the free Career Compass pilot for your Grade {X} students. It takes 15
minutes in class and every student gets a personal report. Shall I send the link? mizaj.pk/schools

## Running a pilot
1. In `/admin`, create 30 Unlock codes, product `career`, organisation = school name.
2. Send the teacher: "Students open mizaj.pk/test/interests, then mizaj.pk/test/personality, then enter their code on
   their result page."
3. A week later send the counsellor the class summary (interest-code mix and stream fit; ask Claude on the server to
   pull it from the database by organisation) and offer the class pack.
