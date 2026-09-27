# CS 690 Assignment 1 Report: Replicating a Controlled Evaluation

## Part 1. Verification evidence

Command:

```text
python -m harness.verify
```

Paste the five `OK` lines here. Keep `results/verification.json` in your repository.

OK: loaded 20 frozen tasks
OK: dataset sha256 5d84176547cb679f4145676d1f4dfd5061bf3b9600904911da8e5700e82eee3b
OK: generated Python executed in Docker sandbox
OK: candidate network probe was blocked
OK: model/configuration metadata written to results/verification.json

## Part 2. Tests and code questions

..................                                                                                                                  [100%]
20 passed in 0.46s

Answer each question in your own words, in about 75 to 150 words. Base every answer on the code in this repository, and name the files and functions you describe.

### Q1. The path of one attempt
I traced task A1-001 (clamp_int) through the code. It starts in load_tasks in harness/tasks.py, which won't even load the file unless its SHA-256 fingerprint matches. From there, run in harness/runner.py wraps the task in PROMPT_TEMPLATE, saves the prompt with _save_prompt, and sends it through _generate_with_retry, which calls OpenAIProvider.generate in harness/provider.py. Once the reply is back, extract_python in harness/grader.py pulls out the code and _save_candidate keeps a copy of it. Then grade_candidate passes it to run_source in harness/sandbox.py. That starts a brand-new container, and docker_entry.py runs the code and tests inside it. The result becomes a row that _append_jsonl writes to raw_results.jsonl. The Docker part makes sense once you remember that no one has read this code. It gets no network, no writable files, and limited memory, so it can't mess with my computer.

### Q2. What is sent and what comes back
Every request, set up in conditions.json and sent by OpenAIProvider.generate, carries the model name and the prompt, plus a few settings. temperature is 1.0, which controls how random the token choices are. reasoning.effort is "none," so there's no hidden thinking step. max_output_tokens is 800, which caps how long (and how expensive) an answer can get. top_p and seed are null, so they're just left out. What comes back gets stored in the Generation class: the answer text, the returned_model, token counts, and the stop_reason, which shows whether the answer finished or got cut off. I didn't expect the returned model to matter, but it does. A name like gpt-5.6-luna can point to different snapshots over time, so the version string is the only real record of what answered.

### Q3. Same prompt, different answers

The three attempts can differ because temperature 1.0 makes the model sample its next token instead of always taking the top choice. There's no seed either, so the randomness isn't pinned down. One different word early on can change the whole program, so one attempt might pass while the next fails. That's on purpose. pass@k is about the odds that at least one of k tries works, and that only means anything if the tries are genuinely separate. As for rerunning my work, the harness leaves a pretty thorough trail: conditions.json, manifest.json with fingerprints for the dataset and config, and raw_results.jsonl, where each row lists the requested and returned model, every sampling setting, run_date_utc, prompt_sha256, and sandbox_image. The exact prompts are in prompts/ and every answer is in candidates/.
### Q4. pass@k by hand

pass_at_k in harness/metrics.py uses 1 − C(n−c, k) / C(n, k). With n = 3 and c = 1, two attempts are wrong.
pass@1 = 1 − C(2,1)/C(3,1) = 1 − 2/3 = 1/3 (about 0.333)
pass@2 = 1 − C(2,2)/C(3,2) = 1 − 1/3 = 2/3 (about 0.667)
The function agreed: 0.33333333333333337 and 0.6666666666666667. The extra digits are just floating-point rounding.
The shortcut gives 1 − (2/3)² = 5/9, about 0.556, which is noticeably lower. The problem is that it acts like you could pick the same attempt twice. But if you choose 2 of 3 attempts, they have to be different ones. There are only three possible pairs, and just one of them is two wrong answers. So the real odds of success are 2 out of 3.


Show your work for pass@1 and pass@2 with n = 3 and c = 1, the values `pass_at_k` returned, and the shortcut `1 - (1 - c/n) ** k` for k = 2.

### Q5. Why whole problems are redrawn

bootstrap_task_ci first gives each task its own pass_at_k score. Then it makes a fake 20-task suite by drawing tasks at random with replacement, so some show up twice and some don't show up at all. It averages that suite, does the whole thing 5000 times with a fixed seed, sorts the results, and uses _percentile to cut 2.5% off each end. The reason it draws whole tasks is that attempts on the same task aren't really independent. If a problem is hard, it tends to fail all three times. Counting 60 attempts as 60 separate data points would make the interval look tighter than it should. test_task_bootstrap_resamples_tasks_not_candidate_rows in tests/test_metrics.py checks this using one task that always passes and one that always fails. Drawing whole tasks, the interval stretches all the way from 0 to 1. Drawing single attempts wouldn't, so the test catches it.

## Part 3. Replication

Part 3 has no written section. Its evidence is the committed `results/experiment/` and `prompts/` folders, and the dollars you spent, which go in the Part 4 table.

## Part 4. Results

Take every number from `results/experiment/summary_A.json` and `results/experiment/summary_B.json`, not from the console. Dollars spent come from the Usage page of your OpenAI account. If your account does not show them, write `not available`. If it shows only one total for the whole run, write the total in row A and `included in A` in row B.

Condition	Requested model	Returned model version	Attempts per task	Total attempts	pass@1	95 percent CI for pass@1	pass@2	Input tokens	Output tokens	Dollars spent
A	gpt-5.6-luna	gpt-5.6-luna	3	60	0.9667	[0.90, 1.00]	0.9833	7146	3793	$0.07
B	gpt-5.6-terra	gpt-5.6-terra	3	60	1.0000	[1.00, 1.00]	1.0000	7146	4311	Included in A


### Memo, no more than 500 words, not counting the table

Address all five items:

1. State the observed ranking by pass@1 point estimate.
2. State whether the uncertainty evidence supports ranking the two conditions.
3. If it does not, include the exact sentence: `The evidence does not support a ranking.`
4. State one external-validity limitation specific to `CS690-Eval20`.
5. State one likely source of variance specific to this experiment, and explain why a rerun, or a classmate's run, gives somewhat different numbers.

Overlapping intervals are not a formal significance test, and you are not asked to run one.

On pass@1, Condition B (gpt-5.6-terra) came out ahead of Condition A (gpt-5.6-luna). B got a perfect 1.0, passing all 60 of its attempts. A scored 0.9667. The pass@2 scores followed the same order, with B at 1.0 and A at 0.9833.
At first that looked like a clear win for B, but I don't think my results actually back that up. A's 95 percent interval for pass@1 is [0.90, 1.00], and B's is [1.00, 1.00], so B's result sits completely inside A's range. I know overlapping intervals aren't a formal test, but the reason for the overlap became obvious when I opened raw_results.jsonl. A only failed two attempts in the entire run, and both were on the same problem, A1-012 (transpose_rectangular). Both failures hit the same list-indexing error on the first test, and A's third attempt on that task passed. Every other task was solved three out of three times by both models. So the whole difference between them comes down to two bad samples on one problem out of twenty. I can't call one model better based on that. The evidence does not support a ranking.
One thing that limits how far these results go is how simple CS690-Eval20 is. Each problem is one short, self-contained function that uses only the standard library, with a clear description and a few assert tests. That's very different from real programming, where you're working in a large codebase across many files, depending on outside libraries, and dealing with requirements that are unclear or keep changing. Both models also scored almost perfectly, so the test set basically ran out of room. Even if one model really were stronger, this set of problems couldn't show it. Doing well here doesn't tell me much about how either model would handle an actual project.
The biggest source of variation in my run is randomness in sampling. Both models ran at temperature 1.0 with no seed, so every attempt can come out different, and with only three attempts per task, a single failure knocks a task's score down by a third. That's exactly what happened on A1-012. If I ran it again, or if a classmate ran it, A could easily pass all three attempts on that task and tie B, or B could miss once somewhere and drop below A. The bootstrap seed is fixed, so the interval math is repeatable, but the answers going into it aren't. The date of the run matters a little too, since the API might serve a different model version later, although in my run the returned models matched what I asked for. My honest takeaway is that both models solved almost everything, and this experiment isn't able to separate them.


## Part 5. Reading a published score, 300 to 400 words

Benchmark chosen (HumanEval, MBPP, LiveCodeBench, or SWE-bench):

Use the benchmark's primary paper or its official documentation for the task definition. Cite evidence for any contamination, saturation, or current-status claim, and date any current-status source.

1. What does it measure?
HumanEval, introduced by Chen et al. (2021) in "Evaluating Large Language Models Trained on Code," is a set of 164 hand-written Python problems. Each problem gives the model a prompt made of a function signature and docstring, the model completes the function, and that function is run against hidden unit tests. It only counts as a success if every hidden test passes. Put as a task: given a short spec for one standalone function, write a body that passes a small set of unit tests. Scores are reported as pass@k, the same estimator my harness uses in pass_at_k. 
arxiv
2. What does it not measure that a software project may depend on?
It doesn't test anything beyond a single function. Real projects mean reading an existing codebase, working across many files, using outside libraries, handling vague requirements, and keeping code readable and maintainable. HumanEval also doesn't reward efficiency, security, or style, only whether a few tests pass.
3. How can a reported score rise without the underlying model becoming better?
The biggest way is weak tests. When Liu et al. (2023) added about 80 times more tests to build HumanEval+, pass@k fell by as much as 19.3 to 28.9 percent across 26 models, and the thin tests had even caused models to be ranked in the wrong order. Training on the problems also inflates scores: in one study, fine-tuning CodeLlama 13B on rephrased versions of the problems raised its HumanEval score from 36.0 to 81.1. Harness choices matter too, like the prompt wording, temperature, and how many samples are allowed. 

4. Could the model have seen the answers already?
The risk is high and well documented. The Stack's authors found HumanEval examples in every one of their training subsets by searching for exact copies of the prompts. Riddell et al. (2024) found that a significant portion of HumanEval had solutions leaked into pretraining data, and that models did much better on problems they'd seen similar solutions for. Since 2021, the problems have been copied all over the internet. I can't prove any specific model was trained on it, but I'd assume exposure is likely. It's also saturated: as of June 2026, frontier models score 96 to 98 percent pass@1, so it can no longer tell top models apart. 

A published HumanEval score can't be swapped in for my CS690-Eval20 result because they use different problems, tests, prompts, sampling settings, and numbers of attempts, and HumanEval's problems have been public for years, while mine came from a frozen course set run under my own harness.


The saturation claim comes from a secondary website, not a paper. If your instructor wants stronger sourcing for current status, check whether the Week 3 slides name a leaderboard you can cite instead.


## References
Chen et al. (2021), Evaluating Large Language Models Trained on Code, arXiv:2107.03374
Liu et al. (2023), Is Your Code Generated by ChatGPT Really Correct?, arXiv:2305.01210
Yang et al. (2023), Rethinking Benchmark and Contamination for Language Models with Rephrased Samples, arXiv:2311.04850
Kocetkov et al. (2022), The Stack: 3 TB of Permissively Licensed Source Code, arXiv:2211.15533
Riddell et al. (2024), Quantifying Contamination in Evaluating Code Generation Capabilities of Language Models, arXiv:2403.04811
Matton et al. (2024), On Leakage of Code Generation Evaluation Datasets, arXiv:2407.07565
BenchmarkingAgents, "HumanEval, MBPP, and LiveCodeBench: Code Benchmarks in 2026," June 12, 2026, benchmarkingagents.com/humaneval (current-status source, accessed September 27, 2026)