import {
  PlayCircle,
  Search,
  MessageSquare,
  Bot,
  Music,
  GitBranch,
  Mail,
  Camera,
  Link2,
  Code2,
  Folder,
  FileText,
  Calculator,
  Terminal,
} from "lucide-react";

const ACTIONS = [
  { label: "ChatGPT", command: "open chatgpt", icon: Bot },
  { label: "Claude", command: "open claude", icon: MessageSquare },
  { label: "YouTube", command: "open youtube", icon: PlayCircle },
  { label: "Google", command: "open google", icon: Search },
  { label: "Spotify", command: "open spotify", icon: Music },
  { label: "GitHub", command: "open github", icon: GitBranch },
  { label: "Gmail", command: "open gmail", icon: Mail },
  { label: "Instagram", command: "open instagram", icon: Camera },
  { label: "LinkedIn", command: "open linkedin", icon: Link2 },
  { label: "LeetCode", command: "open leetcode", icon: Code2 },
  { label: "VS Code", command: "open vscode", icon: Terminal },
  { label: "File Explorer", command: "open file explorer", icon: Folder },
  { label: "Notepad", command: "open notepad", icon: FileText },
  { label: "Calculator", command: "open calculator", icon: Calculator },
];

export default function QuickAccess({ onRun }) {
  return (
    <div className="hud-panel" style={{ flex: 1, minHeight: 0, display: "flex", flexDirection: "column" }}>
      <div className="panel-title">QUICK ACCESS</div>
      <div className="quick-grid">
        {ACTIONS.map(({ label, command, icon: Icon }) => (
          <button
            key={label}
            type="button"
            className="quick-access-btn"
            onClick={() => onRun?.(command)}
          >
            <Icon size={13} />
            {label.toUpperCase()}
          </button>
        ))}
      </div>
    </div>
  );
}
