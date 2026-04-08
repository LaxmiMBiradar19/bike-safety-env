if __name__ == "__main__":
    # 1. SIGNAL START
    # The task name must match your environment name
    task_id = "bike_safety_evaluation"
    print(f"[START] task={task_id}", flush=True)

    try:
        # Reset the environment
        obs = reset()
        
        total_reward = 0
        num_steps = 10  # Run for 10 steps for validation

        for i in range(num_steps):
            # 2. PERFORM STEP
            # Here we just use a simple constant action
            result = step(throttle=0.5, brake=0.0)
            
            # Extract reward and done status from your API response
            # Note: adjust keys if your API returns different names (e.g., 'reward' or 'score')
            reward = result.get("reward", 0.0)
            done = result.get("done", False)
            total_reward += reward

            # 3. SIGNAL STEP (Crucial for the validator)
            print(f"[STEP] step={i} reward={reward}", flush=True)

            if done:
                break

        # 4. SIGNAL END
        # Calculate a final score (usually mean reward or cumulative)
        final_score = total_reward / (i + 1)
        print(f"[END] task={task_id} score={final_score} steps={i+1}", flush=True)

    except Exception as e:
        # If something fails, printing it helps you debug
        print(f"Error during inference: {e}", file=sys.stderr)
