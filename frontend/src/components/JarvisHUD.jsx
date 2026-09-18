import { useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import TopBar from "./TopBar";
import BootSequence from "./BootSequence";
import GreetingPanel from "./GreetingPanel";
import ArcReactor from "./ArcReactor";
import RadialMenu from "./RadialMenu";
import VoiceVisualizer from "./VoiceVisualizer";
import SystemStatus from "./SystemStatus";
import NetworkStatus from "./NetworkStatus";
import QuickAccess from "./QuickAccess";
import WeatherPanel from "./WeatherPanel";
import EventsPanel from "./EventsPanel";
import ActivityLog from "./ActivityLog";
import PowerPanel from "./PowerPanel";
import CommandBar from "./CommandBar";
import { useJarvisState } from "../hooks/useJarvisState";
import { useVoiceInput } from "../hooks/useVoiceInput";

export default function JarvisHUD() {
  const jarvis = useJarvisState();
  const voice = useVoiceInput();

  const handleRadialSelect = (label) => {
    jarvis.pushLog(`RADIAL NODE SELECTED: ${label}`, "info");
  };

  return (
    <>
      <AnimatePresence>
        {!jarvis.booted && <BootSequence onComplete={jarvis.completeBoot} />}
      </AnimatePresence>

      {jarvis.booted && (
        <motion.div
          className="jarvis-hud"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.6 }}
        >
          <TopBar systemOnline={jarvis.systemOnline} voiceActive={voice.active} />

          <div className="hud-left">
            <SystemStatus systemOnline={jarvis.systemOnline} voiceActive={voice.active} />
            <NetworkStatus systemOnline={jarvis.systemOnline} />
            <QuickAccess onRun={jarvis.submitCommand} />
          </div>

          <div className="hud-center">
            <GreetingPanel />
            <div className="reactor-stage">
              <ArcReactor audioLevel={voice.level} />
              <RadialMenu onSelect={handleRadialSelect} />
            </div>
            <div style={{ width: "min(56vh, 620px)" }}>
              <VoiceVisualizer level={voice.level} bins={voice.bins} active={voice.active} />
              <div className="activated-strip">J.A.R.V.I.S. ACTIVATED</div>
            </div>
          </div>

          <div className="hud-right">
            <WeatherPanel />
            <EventsPanel />
            <ActivityLog entries={jarvis.activityLog} />
            <PowerPanel />
          </div>

          <div className="hud-bottom">
            <CommandBar
              onSubmit={jarvis.submitCommand}
              status={jarvis.commandStatus}
              voiceActive={voice.active}
              onToggleVoice={voice.toggle}
            />
          </div>
        </motion.div>
      )}
    </>
  );
}
