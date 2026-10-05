# The Five-State Question — narration script

Format: `# Scene: <class name>` starts a scene, `## <block id>` starts a narration block.
Lines starting with `>` are visual notes and are not spoken. Inline pronunciation hints
use the Kokoro/misaki syntax `[word](/phonemes/)`; subtitles show the plain word.
Every factual claim is taken from the paper (section references in the visual notes);
"proof", "certified computation", "simulation" and "heuristic" are kept distinct.

# Scene: S01_ColdOpen

## c1
> A row of sixteen soldiers; the general at the left end.
Picture a long line of soldiers. At one end stands a general. At some moment the general gives an order, and the goal is for every soldier in the line to fire at exactly the same instant. Not one step too early, and not one step too late.

## c2
> Highlight one soldier and its two neighbours; a small rule book.
Here is the catch. No soldier can see the whole line. Each one sees only the soldier on its left and the soldier on its right. And every soldier follows the same short rule book, no matter how long the line is.

## c3
> The configuration evolves; past rows stack downward into a space-time diagram (Mazoyer's rule, n = 16).
What you are watching is one solution, playing out in time. Each row is one moment, each column is one soldier, and each colour is a state of mind. Time runs downward. Keep an eye on the bottom row.

## c4
> All sixteen cells enter F at time 30. Title card.
Every soldier fires at once. This is the firing squad synchronization problem. It was posed by John [Myhill](/mˈIhɪl/) in 1957, and almost seventy years later, one very simple question about it is still open.

## c5
> Subtitle: its history, why it is hard, and what we could prove.
This video is about that question: where it came from, why it is so hard, and what we were able to prove about it.

# Scene: S02_Puzzle

## p1
> A line of n cells; the states as coloured tiles: L, G, A, B, F.
Let us make the rules precise. We have a row of n cells. Each cell is a tiny machine that is always in one of finitely many states, and time moves in discrete steps.

## p2
> Neighbourhood (left, self, right) → rule table → new state. Borders shown as a star.
At every step, every cell looks at three things: the state of its left neighbour, its own state, and the state of its right neighbour. The cells at the two ends see a border instead of a neighbour. A single lookup table, called the rule, gives the new state.

## p3
> Example from the paper (Fig. 3): G L L → A in the rule delta fourteen.
For example, if a cell is quiescent, its left neighbour is the general, and its right neighbour is quiescent, the table might say: become A. All cells use the same table, and they all update at the same time.

## p4
> Initial configuration G L L … L; the quiescence conditions L L L → L and L L * → L; the goal.
At time zero, the leftmost cell is the general and every other cell is quiescent, which just means asleep. A sleeping cell between sleeping cells stays asleep. The goal is a table such that, for every length n, all cells enter the firing state at the same moment, and no cell fires before that moment.

## p5
> Lines of many lengths; the number of states stays fixed; zoom out to a very long line.
The hard part is the phrase "for every length". The number of states is fixed in advance, say five or six. But the line might have a million cells, and no soldier can count to a million with six states of mind. Somehow the line has to measure itself, using nothing but conversations between neighbours.

## p6
> "Take a moment to think about it."
If you have never seen this puzzle before, it is worth pausing to think about how you would solve it.

# Scene: S03_SpeedLimit

## s1
> The front of the wave: cell i wakes up at time i minus one at the earliest.
Before looking at solutions, let us ask how fast a solution could possibly be. Since each cell only sees its neighbours, information travels at most one cell per step. The news of the order spreads from the general like a wave, and it reaches the far end at time n minus one at the earliest.

## s2
> Two diagrams, lengths 6 and 9, same rule; the region t + i ≤ 10 is highlighted on both (paper, Fig. 4).
Now here is the key observation. Run the same rule on a line of length six and on a line of length nine. For a while the two pictures are identical, cell for cell. In fact they agree for longer than you might think. The short line only discovers that it has an end when its last cell feels the border, and that discovery travels back at most one cell per step.

## s3
> The echo runs back along the anti-diagonal t + i = 2n − 2 and reaches cell 1 at time 2n − 2.
So the first soldier learns where the line ends after n minus one steps for the wave to go out, plus n minus one steps for the echo to come back: at time two n minus two. Before that moment, it cannot tell its own line apart from a longer one.

## s4
> If the line of length n fired at T < 2n − 2, the first cell of every longer line would fire at T too, while its far end is still asleep.
That gives a speed limit. If the line of length n fired at some earlier time, the first soldier would fire at that same time in every longer line, including lines so long that their far end is still asleep. That is not a synchronized firing at all.

## s5
> "2n − 2"; Goto 1962, Waksman 1966; definition of a minimal-time solution.
So two n minus two is a hard lower bound. The remarkable fact, shown by [Goto](/ɡˈOtO/) in 1962 and by Waksman in 1966, is that this bound can actually be reached. Rules that synchronize every line of length n at exactly time two n minus two are called minimal-time solutions, and they are what this video is about.

# Scene: S04_History

## h1
> A scoreboard: number of states.
Once minimal time was possible, a new game began: how few states do you need? Think of it as a kind of golf, where your score is the number of states in your rule book.

## h2
> Timeline: Waksman 16 (1966), Balzer 8 (1967), Gerken 7 (1987), Mazoyer 6 (1987).
Waksman's solution used sixteen states. In 1967 Robert Balzer brought this down to eight. Twenty years later, [Hans-Dieter](/hˈɑns dˈitəɹ/) [Gerken](/ɡˈɛɹkən/) found a solution with seven states, and in the same year, 1987, Jacques [Mazoyer](/mˌɑzwɑjˈA/) found one with just six. That record still stands.

## h3
> Four states: Balzer 1967 (search), Yunès 1993 (lengths 2..9 suffice), Sanders 1994 (corrected search).
What about fewer? Balzer also ran a computer search and reported that no four-state minimal-time solution exists. [Jean-Baptiste](/ʒˈɑn bɑtˈist/) [Yunès](/junˈɛs/) repeated the search in 1993 and observed that the lines of lengths two to nine already rule out four states. In 1994 Peter Sanders found that Balzer's backtracking was incomplete, and he confirmed the result with a corrected search.

## h4
> Scoreboard: 4 impossible, 5 open, 6 solved.
So four states are impossible and six are possible. And five? Nobody knows. The question has been open since 1987, and the surveys list it as open. Many different six-state solutions are known today, but nobody has found a five-state solution, and nobody has proved that none exists.

## h5
> Balzer's conditional result (paper, Section 6.4).
Balzer did report one result about five states. According to his program, no five-state solution satisfies four extra conditions, conditions that his own eight-state solution satisfies. We will come back to that claim, because we can now check it with a certificate.

# Scene: S05_HowSolutionsWork

## w1
How can a line of cells with six states of mind synchronize itself in exactly the right time? The classical idea is divide and conquer.

## w2
> Schematic: hare (speed 1) and tortoise (speed 1/3) leave the general; the hare bounces at the right border.
Here is the textbook version, which you can find in Minsky's book from 1967. The general sends out two signals: a fast one, the hare, which moves one cell per step, and a slow one, the tortoise, which moves one cell every three steps. The hare bounces off the far end and comes back. Where does it meet the tortoise?

## w3
> They meet at the middle at time 3(n − 1)/2; the hare has covered three times the tortoise's distance.
When they meet, the hare has travelled three times as far as the tortoise, once out to the end and part of the way back. A line of algebra shows that this happens exactly in the middle of the line. The meeting point becomes a new general, and now each half is a firing squad of its own, with a general at each end.

## w4
> Recursion into halves and quarters; total about 3n steps.
Repeat the trick in each half, then in each quarter, and so on, until every soldier is a general at the same moment, and everybody fires. Adding up the times gives about three n steps. Correct, but not minimal.

## w5
> Signals of speeds 1/3, 1/7, 1/15 from the general; the reflected signal meets them near n/2, n/4, n/8 (paper, Section 3.6).
To reach two n minus two, the minimal-time constructions launch signals of speeds one third, one seventh, one fifteenth, and so on, all at once. The signal reflected from the far end meets them near the half, the quarter and the eighth of the line, at exactly the moments when the pieces between them can be synchronized recursively, so that all pieces fire together at time two n minus two.

## w6
> Mazoyer's six-state rule on a line of 40 cells, computed from Duprat's table.
Here is Mazoyer's six-state solution on a line of forty cells, computed directly from its rule table. You can see the recursive structure: the line is cut into smaller and smaller pieces, and every piece finishes at the same moment. Its correctness for every length has been proved, and that proof has even been checked by a computer.

## w7
> Mazoyer (1996): all his solutions divide the line recursively, at ratios in [1/2, 1).
Mazoyer observed that all the solutions he had constructed divide the line recursively in this way. Keep that in mind. Our results do not force this strategy, but they show that some non-periodic structure must appear exactly where these signals run.

# Scene: S06_Haystack

## f1
> The five-state rule table: 5 · 4 · 5 neighbourhoods, minus 4 unused, minus 2 fixed = 94 free entries.
So why not search for a five-state solution by computer? Let us count. A five-state rule is a table with ninety-four free entries, and each entry can be any of the five states. That makes five to the ninety-fourth possible tables, a number with sixty-six digits.

## f2
> 4^43 ≈ 7.7 · 10^25 against 5^94 ≈ 5.0 · 10^65.
For four states there are four to the forty-third tables, about ten to the twenty-sixth. Going from four states to five adds roughly forty orders of magnitude.

## f3
> A search tree with pruning; Balzer: 3 hours, about 570,000 partial rules; Sanders: about 10^16 times the age of the universe.
Of course, nobody checks tables one at a time. A clever search fills in entries only when they are needed and abandons a partial table as soon as some line misbehaves. That is how the four-state case was settled. For five states it does not come close. Balzer stopped his five-state search after three hours and about five hundred seventy thousand partial rules. Sanders estimated that a five-state search on his parallel machine, with sixteen thousand processors, would take about ten to the sixteenth times the age of the universe.

## f4
So brute force is out. To make progress you need mathematics that shrinks the haystack: necessary conditions that every five-state solution must satisfy. That is what we went looking for.

# Scene: S07_HalfLine

## l1
> Recall the agreement region.
Our starting point is the speed-limit argument, taken seriously. Every line behaves exactly like an infinitely long line, a half-line, until the echo of its right end comes back.

## l2
> The half-line diagram of delta fourteen grows.
So picture the half-line: one general, followed by infinitely many sleeping soldiers. Run the rule, and you get a single space-time diagram, which is the same for every length.

## l3
> The line of length 12 on top of the half-line: identical above the anti-diagonal t + i = 22; the reflected triangle below it.
Now take the line of length n. Above this anti-diagonal, the line of length n and the half-line agree, cell for cell. The only part that is specific to the length n is this triangle at the right end, where the echo of the border is processed. We call it the reflected triangle.

## l4
> The two input anti-diagonals t + i = 2n − 3 and 2n − 2 (lemma 3.1, determinacy).
And here is the nice part. Everything the triangle knows about the half-line comes in through its upper edge: two anti-diagonals of cells. Everything inside the triangle is a function of those two anti-diagonals alone.

## l5
> Triangles for several lengths hanging off one half-line.
So a minimal-time solution is really one infinite picture, the half-line, together with one triangle for each length, each reading two anti-diagonals of that picture and firing at exactly the right moment. This lets us ask questions about the half-line alone, which is a single object, instead of infinitely many lines.

# Scene: S08_Pumping

## u1
> The reflected triangle in relative coordinates; the firing of the right end (star) and its cone of dependence (lemma 3.2).
Here is the first barrier. Look at the last cell of the line of length n. It must fire at time two n minus two. Which input cells can influence that event? Trace back its cone of dependence. It covers roughly the right half of the two input anti-diagonals, about n over two cells.

## u2
> A longer line n' reaches the same relative cell at time n' + n − 2, before 2n' − 2.
Now take a longer line, of length n prime. Its triangle passes through the same relative position, the same distance from its right end and the same time after the echo started. But for the longer line, that moment is too early to fire. If the two input words agreed on the whole cone, the right end of the longer line would fire too early.

## u3
> Statement of the pumping lemma (lemma 3.3).
So in every minimal-time solution, the input words of two different lengths must differ somewhere on this cone. We call this the pumping lemma, because it works like the pumping arguments of automata theory. Its strength is that it only talks about the half-line: no triangle has to be computed.

## u4
> Ride along with the front: depth-rows behind the front, each eventually periodic.
What does it force? Ride along with the front of the wave. Seen from the front, each depth behind it is a row of cells, driven by the rows ahead of it, and every such row eventually repeats with some period. If all the rows that the cone touches had already settled into their periodic patterns, then two lengths that differ by a common period would show identical input words on the cone. And that is forbidden.

## u5
> Theorem 3.4: limsup θ(j)/j ≥ 3/2; the line i = t/3.
Work out where the far end of the cone lies, and you get our first theorem. In every minimal-time solution, the non-periodic part of the half-line must reach the line where the cell index is one third of the time. Something has to keep happening at least as far out as a signal of speed one third.

## u6
> Mazoyer's half-line: the periodic zone starts at the line i = t/2, beyond i = t/3.
That is exactly the speed of the tortoise. In the classical constructions the slow signal was a design choice; the barrier explains why some non-periodic structure must reach that line in every minimal-time solution. In Mazoyer's solution, the periodic zone behind the front ends at a signal of speed one half, comfortably within the bound.

# Scene: S09_LeftBorder

## e1
> The lower left corner of a line: chains behind the reflected wave (paper, Fig. 6).
The second barrier lives at the other end, at the left border. Think about the soldiers next to the general's position. The reflected wave reaches them only at the very end, just before the firing time. Whatever lets them fire at exactly the right moment must be read off what the half-line has stored around them, by a narrow band of anti-diagonals right behind the wave.

## e2
> The band as a finite automaton; a periodic stretch; pigeonhole: a repeated band state.
That band behaves like a finite automaton reading the half-line. And a finite automaton cannot count along a long periodic stretch. By the pigeonhole principle it falls into a loop, and then it cannot tell where it is. If the half-line were periodic near the border over a long stretch, some soldier near the border would fire at the wrong time.

## e3
> Lemma 3.5 with its explicit bound.
This is our left-border lemma, and it comes with an explicit bound on how long such a periodic stretch can be.

## e4
> Theorem 3.6 (no periodic wedge at the border) and corollary 3.8 (never eventually regular).
From it we get the second theorem: the half-line of a minimal-time solution can never be periodic in any wedge at the left border. In particular, it is never eventually regular: it cannot settle into finitely many periodic regions separated by straight signals. In the classical constructions, this role is played by the ever slower signals and the recursive division points that pile up at the border.

## e5
> The half-line of delta twelve: front, wake, a boundary of speed exactly 1/3, a periodic region of A and L (corollary 6.2).
Here is why this matters. Our solvers found five-state rules, delta twelve and delta thirteen, that synchronize every line up to length twelve and thirteen. Their common half-line looks like this: a wake behind the front, and behind a boundary of speed exactly one third, a perfectly periodic pattern of A's and L's. It sits exactly at the limit of the speed one third barrier, so it passes. But it is periodic in a wedge at the border, so the left-border lemma rules it out. At length five hundred eighteen, the lemma would require two hundred fifty-seven to be at most two hundred fifty-six. No completion of this half-line can be a solution.

# Scene: S10_FourStates

## r1
> Propositional encoding: variables for the table entries and the cells, clauses for the rule.
Conditions like these are cheap to test, so we turned the bounded problem into propositional logic: one large Boolean formula, which has a solution whenever some rule synchronizes a given set of lengths in minimal time, and which also contains consequences of the barriers. Then we hand the formula to a [SAT](/sˈæt/) solver. If the solver finds no solution, no such rule exists.

## r2
> Validation: Mazoyer's rule, extracted from Jean Duprat's formal proof, satisfies the encoding.
Before trusting the encoding, we tested it on Mazoyer's solution, extracted mechanically from [Jean](/ʒˈɑn/) [Duprat's](/dupɹˈɑz/) formal proof of its correctness. The encoding accepts it, as it must.

## r3
> CaDiCaL: unsatisfiable in 51 seconds (theorem 5.1).
For four states, the solver [CaDiCaL](/kˈædikˌæl/) shows in fifty-one seconds that no four-state rule synchronizes all lines of lengths two to nine in minimal time. But why should you trust a solver? Solvers are large programs, and the earlier proofs of the four-state result rested on the correctness of search programs. One of them, as we saw, had a flaw.

## r4
> Formula → solver → LRAT certificate (177 MB) → lrat-check: VERIFIED in 5.7 s.
So the solver also writes down its reasoning, as a proof certificate in the [LRAT](/ˈɛl ˈɑɹ ˈA tˈi/) format, a hundred seventy-seven megabytes in this case. An independent checker, a small program that only has to verify each step, confirms it in under six seconds. You do not have to trust the solver or our search code; you have to trust the formula and a small checker.

## r5
> Four states: Balzer 1967, Yunès 1993, Sanders 1994, certified now. Search tree estimate: about 25 nodes.
So the four-state lower bound, first claimed in 1967, now comes with a certificate that anyone can check in seconds. And by our estimate, the whole four-state search tree has only about twenty-five nodes.

# Scene: S11_Frontier

## d1
For five states, the same tools run into a wall, and the wall is made of very lucky rules.

## d2
> Delta fourteen on lines of lengths 10 to 14: each fires at exactly 2n − 2.
Meet delta fourteen, a five-state rule that our solver found. On a line of length ten, it fires at time eighteen, all at once. Length eleven: perfect. Twelve, thirteen, fourteen: perfect every time, at exactly two n minus two.

## d3
> Length 15: cells 13, 14 and 15 fire at time 22 instead of 28.
Now length fifteen. The last three cells fire at time twenty-two, six steps too early. Delta fourteen synchronizes every line up to length fourteen, and then it fails. We found four more five-state rules that do the same.

## d4
> Every refutation along these lines needs lines of length at least 15.
That is sobering. Any impossibility proof of this kind must look at lines of length at least fifteen, because shorter lines cannot tell delta fourteen apart from a real solution.

## d5
> The half-line of delta fourteen: irregular, essentially the elementary rule 22.
And its half-line is nothing like the clean recursive structures of the known solutions. It is chaotic. It is essentially the elementary cellular automaton rule twenty-two, a sea of irregular triangles, and it passes both of our barriers, at least in the ranges we checked.

# Scene: S12_Germs

## g1
> The region t + i ≤ 78 of a half-line; count the distinct neighbourhoods (complexity c_78).
This suggests turning the search around. A half-line uses only some entries of the rule table: the neighbourhoods that actually occur in it. Count the distinct neighbourhoods that occur below the anti-diagonal t plus i equals seventy-eight, and call that number the complexity of the half-line. Mazoyer's solution has complexity fifty-seven, and delta twelve has twenty-two.

## g2
> A depth-first search: 10^8 nodes, 244 germs of complexity at most 14; an independent program finds the same 244.
Half-lines of low complexity are rare, so we can list them all and try to eliminate each one. A depth-first search through a hundred million nodes finds two hundred forty-four candidates of complexity at most fourteen that pass the basic tests, and an independent re-implementation finds the same two hundred forty-four.

## g3
> 230 refuted by one certified solver call (lengths 2 to 10); 14 refuted by the left-border lemma.
For two hundred thirty of them, a single certified solver call shows that they cannot be completed even for the lines up to length ten. The remaining fourteen are periodic near the border, and the left-border lemma eliminates them.

## g4
> Proposition 6.4: c_78 ≥ 15. Funnel for complexity ≤ 16: 9,787 → 963 → 32 → 24 → 16.
The result: every five-state minimal-time solution uses at least fifteen distinct neighbourhoods on its half-line below anti-diagonal seventy-eight. Running the same pipeline up to complexity sixteen, out of nine thousand seven hundred eighty-seven half-lines only sixteen survive, and as far as our certificates can tell, all of them are irregular. One of them is the half-line of delta fourteen.

## g5
So at low complexity, the orderly half-lines are all gone, and what remains looks like chaos, which is exactly where our barriers have nothing to grab onto.

# Scene: S13_Balzer

## z1
> Image solution: mirror the diagram and rename the states by a fixed involution; Balzer's four conditions.
Now back to Balzer's claim about five states. His eight-state solution has an elegant extra property, which he called an image solution: reflect the rule left to right, rename the states by a fixed swap, and you get the same rule back. Together with three conditions on the general, a cell between two generals becomes a general, a general stays a general, and the firing is triggered only by generals, this makes four conditions.

## z2
> Balzer (1967, p. 37): "the weakest conditions we found which enabled the program to prove that no five state minimal time solution existed."
Balzer reported that, with these conditions, his program proved that no five-state minimal-time solution exists, and that it could not prove the same for six states. It came from the same kind of backtracking search that Sanders later found to be incomplete, so the claim deserved an independent check.

## z3
> Results: involution (A B) unsatisfiable at N = 10; (L A), (L B) at N = 9; identity at N = 12 (LRAT 3.1 GB, checked in 66 s).
We added the four conditions to our formula as extra clauses. Result: no five-state rule satisfying Balzer's conditions synchronizes all lines of lengths two to twelve, even under a weaker reading of the conditions, and every case comes with a checked certificate. The largest certificate is three point one gigabytes, and the checker verifies it in sixty-six seconds.

## z4
> Symmetric rules satisfying the conditions exist for all lengths up to 11.
And length twelve is really needed: symmetric rules satisfying the conditions synchronize every line up to length eleven. So Balzer's claim from 1967 is correct.

## z5
> Six states: rules satisfying the conditions for all lengths up to 13 (all four involution types), up to 14 (two types).
With six states the picture changes. Rules satisfying the conditions exist for all lines up to length thirteen, for every type of swap, and up to length fourteen for two of them. Whether the conditions exclude six states is open, just as it was for Balzer.

# Scene: S14_Outlook

## o1
> The scoreboard again.
So where does this leave the five-state question? Four states: impossible, now with a certificate. Six states: possible since 1987. Five: still open.

## o2
> Search-tree estimates (log scale): about 25 nodes for four states; 10^11 to 10^19 for five. What every five-state solution must satisfy.
Our estimates make the gap concrete: about twenty-five nodes in the four-state search tree, against something like ten to the eleventh to ten to the nineteenth for five states. What we do know is that any five-state solution needs a half-line that is never eventually regular, whose non-periodic part reaches the line of speed one third, with at least fifteen distinct neighbourhoods below anti-diagonal seventy-eight, and that refutations along our lines need lines of length at least fifteen.

## o3
> The mirrored construction (paper, Section 7): a heuristic, not a theorem.
There is also a heuristic picture of why five is hard. At the right end of every line, the echo of the border has to run a mirrored synchronization, on the background left behind the front instead of on sleeping cells. A five-state solution would have to perform both constructions, the direct one and the mirrored one, with the same four working states. We regard this tension as the structural reason why five states are hard, but turning it into a proof is open.

## o4
> Heuristic: about 2^(181 − N²/2) completions survive the lengths up to N, so chaotic germs should run out near N ≈ 20.
A rough count suggests that chaotic candidates like delta fourteen should run out somewhere around length twenty. But that is a heuristic, and we have not been able to turn it into a proof either.

## o5
> Open problems (paper, Section 7).
So here are the questions we would love to see answered. Does a five-state minimal-time solution exist? Is there a necessary condition that constrains the reflected triangles themselves, not only the half-line? And if five-state rules stop working at some length, at which one? We know it is beyond fourteen.

## o6
> Closing: the line of soldiers fires one last time.
[Myhill's](/mˈIhɪlz/) puzzle is almost seventy years old. Its solutions are among the most elegant constructions in computing, and between four and six, one number is still waiting. Maybe the answer is a hidden five-state solution, chaotic and strange. Maybe it is an impossibility proof that finally captures why five is not enough. Either way, we hope you find the question as irresistible as we do.

## o7
> Credits: the paper, its authors, and the tools.
This video is based on our paper, "Towards five-state minimal-time firing squads". Thanks for watching.
