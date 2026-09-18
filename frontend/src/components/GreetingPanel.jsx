import { motion } from "framer-motion";

const USER_NAME = "MADHAV";

function getGreeting(hour) {
  if (hour < 5) return "GOOD NIGHT";
  if (hour < 12) return "GOOD MORNING";
  if (hour < 17) return "GOOD AFTERNOON";
  if (hour < 21) return "GOOD EVENING";
  return "GOOD NIGHT";
}

export default function GreetingPanel() {
  const greeting = getGreeting(new Date().getHours());

  return (
    <motion.div
      className="greeting-panel"
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.7, delay: 0.2 }}
    >
      <div className="greeting-line">{greeting}</div>
      <div className="greeting-name">{USER_NAME}</div>
      <div className="greeting-sub">I'M JARVIS &mdash; HOW CAN I ASSIST YOU TODAY?</div>
    </motion.div>
  );
}
