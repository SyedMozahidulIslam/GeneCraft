from __future__ import annotations
import logging, math, time
from typing import Optional, TYPE_CHECKING
import pygame
from engine.config_manager import ConfigManager
from engine.event_bus import EventBus, GameEvent

if TYPE_CHECKING:
    from engine.game_engine import GameEngine, GameState

logger = logging.getLogger(__name__)

_BG      = (13, 17, 23)
_SURF    = (22, 27, 34)
_ACCENT  = (0, 255, 136)
_ACCENTB = (0, 170, 255)
_TEXT    = (230, 237, 243)
_MUTED   = (139, 148, 158)
_BORDER  = (48, 58, 72)
_RED     = (255, 68, 68)
_AMBER   = (255, 170, 0)
_PURPLE  = (180, 80, 255)


def _font(size):
    try:    return pygame.font.SysFont("consolas,monospace,courier", size)
    except: return pygame.font.Font(None, size + 4)


class UIEngine:
    def __init__(self, config, bus, screen, engine):
        self.config  = config
        self.bus     = bus
        self.screen  = screen
        self.engine  = engine
        self._W, self._H = screen.get_size()

        self._f_lg   = _font(22)
        self._f_md   = _font(15)
        self._f_sm   = _font(12)
        self._f_tiny = _font(10)

        self._notifications = []
        self._active_overlay = None
        self._screens_ready  = False
        self._bottom_buttons = []
        self._world_renderer = None
        self._notif_duration = (config.get("ui.notification_duration_ms") or 4000) // 16

        bus.subscribe("achievement:unlocked", self._on_achievement)
        bus.subscribe("disaster:started",     self._on_disaster)
        bus.subscribe("species:extinct",      self._on_extinct)
        bus.subscribe("evolution:adaptation", self._on_adaptation)
        bus.subscribe("species:speciation",   self._on_speciation)
        bus.subscribe("research:unlocked",    self._on_research)
        logger.info("UIEngine initialised (%dx%d).", self._W, self._H)

    # ── Layout ─────────────────────────────────────────────────────────────
    @property
    def top_bar_rect(self):    return pygame.Rect(0, 0, self._W, 44)
    @property
    def bottom_bar_rect(self): return pygame.Rect(0, self._H-52, self._W, 52)
    @property
    def side_panel_rect(self): return pygame.Rect(self._W-240, 44, 240, self._H-96)
    @property
    def viewport_rect(self):   return pygame.Rect(0, 44, self._W-240, self._H-96)

    # ── Lifecycle ──────────────────────────────────────────────────────────
    def on_resize(self, w, h):
        self._W, self._H = w, h
        self._screens_ready = False
        self._world_renderer = None

    def on_state_change(self, old, new): pass

    def handle_event(self, event):
        for btn in self._bottom_buttons:
            self._btn_handle(btn, event)
        if self._world_renderer:
            self._world_renderer.handle_event(event)

    # ── Master Render ──────────────────────────────────────────────────────
    def render(self, state, world_tick):
        from engine.game_engine import GameState
        if state == GameState.MAIN_MENU:
            self._render_main_menu(world_tick)
        else:
            self._ensure_game_ui()
            self._render_game(world_tick, paused=(state == GameState.PAUSED))
        self._render_notifications()

    # ── Main Menu ──────────────────────────────────────────────────────────
    def _render_main_menu(self, tick):
        s = self.screen
        s.fill(_BG)
        # Grid
        for x in range(0, self._W, 40): pygame.draw.line(s, (20,28,38), (x,0), (x,self._H))
        for y in range(0, self._H, 40): pygame.draw.line(s, (20,28,38), (0,y), (self._W,y))

        # Logo
        logo_f = _font(54)
        logo   = logo_f.render("GeneCraft", True, _ACCENT)
        s.blit(logo, (self._W//2 - logo.get_width()//2, self._H//5))
        tag = self._f_sm.render("Shape Genes. Control Evolution. Build a Living World.", True, _MUTED)
        s.blit(tag, (self._W//2 - tag.get_width()//2, self._H//5 + 68))

        # Animated DNA helix
        t = time.time()
        cy = self._H//5 + 100
        for i in range(18):
            ang = i * 0.5 + t
            x1 = self._W//2 + int(math.cos(ang)*55)
            x2 = self._W//2 + int(math.cos(ang+math.pi)*55)
            yp = cy + i*7
            c1 = (0,200,100) if i%2==0 else (0,140,255)
            c2 = (0,140,255) if i%2==0 else (0,200,100)
            pygame.draw.circle(s, c1, (x1, yp), 4)
            pygame.draw.circle(s, c2, (x2, yp), 4)
            if i>0: pygame.draw.line(s, (30,50,40), (self._W//2, yp-7), (self._W//2, yp), 1)

        # Menu buttons
        bw, bh = 280, 48
        bx = self._W//2 - bw//2
        items = [
            ("▶  New Campaign",  "campaign", _ACCENT,  (20,35,28)),
            ("◈  Sandbox Mode",  "sandbox",  _ACCENTB, (20,26,38)),
            ("⟳  Load Game",     "load",     _MUTED,   _SURF),
            ("⚙  Settings",      "settings", _MUTED,   _SURF),
            ("✕  Quit",          "quit",     _RED,     (30,16,16)),
        ]
        mouse_pos = pygame.mouse.get_pos()
        mouse_down = pygame.mouse.get_pressed()[0]
        for i, (label, action, accent, bg) in enumerate(items):
            by = self._H//2 + 20 + i*(bh+10)
            r  = pygame.Rect(bx, by, bw, bh)
            hovered = r.collidepoint(mouse_pos)
            fill = (int(bg[0]*1.4), int(bg[1]*1.4), int(bg[2]*1.4)) if hovered else bg
            fill = tuple(min(255,v) for v in fill)
            pygame.draw.rect(s, fill, r, border_radius=7)
            pygame.draw.rect(s, accent, r, width=1+(1 if hovered else 0), border_radius=7)
            if hovered and i==0:
                for gr in range(5,0,-1):
                    gs = pygame.Surface((bw+gr*2,bh+gr*2), pygame.SRCALPHA)
                    pygame.draw.rect(gs, (*_ACCENT, 15), gs.get_rect(), border_radius=9)
                    s.blit(gs, (bx-gr, by-gr))
            lt = self._f_md.render(label, True, _TEXT)
            s.blit(lt, (bx + bw//2 - lt.get_width()//2, by + bh//2 - lt.get_height()//2))
            if hovered and mouse_down:
                self._menu_action(action)

        ver = self._f_tiny.render("v1.0.0  |  GeneCraft Studio  |  © 2024", True, (45,55,70))
        s.blit(ver, (self._W - ver.get_width() - 10, self._H - 18))

    # ── Game Setup ────────────────────────────────────────────────────────
    def _ensure_game_ui(self):
        if self._screens_ready: return
        self._setup_world_renderer()
        self._setup_bottom_buttons()
        self._screens_ready = True

    def _setup_world_renderer(self):
        from ui.renderer.world_renderer import WorldRenderer
        self._world_renderer = WorldRenderer(
            config=self.config, registry=self.engine.species_registry,
            viewport=self.viewport_rect)
        if self.engine.world and self.engine.world.tiles:
            self._world_renderer.attach_world(self.engine.world)

    def _setup_bottom_buttons(self):
        bh = 36; by = self._H - 44; bx = 10
        labels = [("🧬 Gene Lab","gene_lab"),("🔬 Research","research"),
                  ("📊 Statistics","stats"),("📖 Encyclopedia","encyclopedia"),
                  ("⚡ Events","events"),("💾 Save","save")]
        self._bottom_buttons = []
        for label, action in labels:
            bw = 128
            self._bottom_buttons.append({"rect":pygame.Rect(bx,by,bw,bh),"label":label,
                                          "action":action,"hovered":False})
            bx += bw + 5

    # ── Game Render ───────────────────────────────────────────────────────
    def _render_game(self, tick, paused=False):
        s = self.screen
        if self._world_renderer:
            if self.engine.world and self.engine.world.tiles and not self._world_renderer._world:
                self._world_renderer.attach_world(self.engine.world)
            self._world_renderer.render(s, tick)
        self._render_top_bar(tick, paused)
        self._render_side_panel(tick)
        self._render_bottom_bar()
        if self._active_overlay:
            self._render_overlay(self._active_overlay, tick)
        if paused:
            ov = pygame.Surface((self._W,self._H), pygame.SRCALPHA)
            ov.fill((0,0,0,90)); s.blit(ov,(0,0))
            pt = self._f_lg.render("⏸  PAUSED  —  Press SPACE to resume", True, _ACCENT)
            s.blit(pt, (self._W//2 - pt.get_width()//2, self._H//2 - 15))

    def _render_top_bar(self, tick, paused):
        s = self.screen; r = self.top_bar_rect
        pygame.draw.rect(s, (14,20,28), r)
        pygame.draw.line(s, _ACCENT, (0, r.bottom), (self._W, r.bottom), 1)

        logo = self._f_md.render("🧬  GENECRAFT", True, _ACCENT)
        s.blit(logo, (12, r.centery - logo.get_height()//2))

        if self.engine.world and self.engine.world.tiles:
            season = self.engine.world.season.upper()
            year   = tick // 365 + 1
            day    = tick % 365 + 1
            info   = f"Year {year}  ·  Day {day}  ·  {season}"
            it = self._f_sm.render(info, True, _MUTED)
            s.blit(it, (self._W//2 - it.get_width()//2, r.centery - it.get_height()//2))

        if self.engine.research:
            rp = int(self.engine.research.points)
            rt = self._f_sm.render(f"🔬 {rp} RP", True, _ACCENTB)
            s.blit(rt, (self._W - 130, r.centery - rt.get_height()//2))

        if self.engine.config.get("game.debug_mode"):
            fps = self.engine.clock.get_fps() if self.engine.clock else 0
            ft  = self._f_tiny.render(f"{fps:.0f}fps", True, (70,80,95))
            s.blit(ft, (self._W - 52, 4))

    def _render_side_panel(self, tick):
        s = self.screen; r = self.side_panel_rect
        pygame.draw.rect(s, (14,20,28), r)
        pygame.draw.line(s, _BORDER, (r.x, r.y), (r.x, r.bottom))
        y = r.y + 10

        hdr = self._f_sm.render("ECOSYSTEM", True, _ACCENT)
        s.blit(hdr, (r.x+10, y)); y += 24

        if self.engine.statistics and self.engine.statistics.last_snapshot:
            snap = self.engine.statistics.last_snapshot
            rows = [
                ("Population",   f"{snap.get('total_population',0):,}",     _TEXT),
                ("Species",      str(snap.get('species_count',0)),          _ACCENTB),
                ("Biodiversity", f"{snap.get('biodiversity',0.0):.3f}",     _ACCENT if snap.get('biodiversity',0)>0.5 else _AMBER),
                ("Extinctions",  str(snap.get('extinction_events',0)),      _RED),
                ("Evolutions",   str(snap.get('evolution_events',0)),       _ACCENTB),
                ("Disasters",    str(snap.get('predation_events',0)),       _AMBER),
            ]
            for label, val, col in rows:
                lt = self._f_tiny.render(label+":", True, _MUTED)
                vt = self._f_tiny.render(val, True, col)
                s.blit(lt, (r.x+10, y)); s.blit(vt, (r.right-vt.get_width()-10, y)); y += 18

        pygame.draw.line(s, _BORDER, (r.x+8, y+4), (r.right-8, y+4)); y += 14

        sp_hdr = self._f_sm.render("SPECIES", True, _ACCENT)
        s.blit(sp_hdr, (r.x+10, y)); y += 22

        old_clip = s.get_clip()
        s.set_clip(pygame.Rect(r.x, y, r.width, r.bottom-y-6))

        snap = (self.engine.statistics.last_snapshot if self.engine.statistics else {}) or {}
        for sp_data in (snap.get("species",[]) or [])[:16]:
            if y > r.bottom - 20: break
            color = tuple(sp_data.get("color",[200,200,200]))
            pygame.draw.circle(s, color, (r.x+16, y+7), 5)
            nt = self._f_tiny.render(sp_data["name"][:17], True, _TEXT)
            pt = self._f_tiny.render(str(sp_data["population"]), True, _MUTED)
            s.blit(nt, (r.x+26, y)); s.blit(pt, (r.right-pt.get_width()-8, y)); y += 18

        s.set_clip(old_clip)

    def _render_bottom_bar(self):
        s = self.screen; r = self.bottom_bar_rect
        pygame.draw.rect(s, (14,20,28), r)
        pygame.draw.line(s, _ACCENT, (0, r.y), (self._W, r.y), 1)

        mp = pygame.mouse.get_pos()
        for btn in self._bottom_buttons:
            br = btn["rect"]; hov = br.collidepoint(mp)
            bg  = (30,42,35) if hov else (20,28,36)
            acc = _ACCENT if hov else _BORDER
            pygame.draw.rect(s, bg, br, border_radius=5)
            pygame.draw.rect(s, acc, br, width=1, border_radius=5)
            lt = self._f_tiny.render(btn["label"], True, _TEXT if hov else _MUTED)
            s.blit(lt, (br.x + br.w//2 - lt.get_width()//2, br.y + br.h//2 - lt.get_height()//2))

        # Speed controls
        speeds = [("⏸","paused"),("1×","normal"),("2×","fast"),("3×","faster"),("5×","ultra")]
        sx = self._W - 265
        for label, key in speeds:
            sr = pygame.Rect(sx, r.y+8, 46, 28)
            pygame.draw.rect(s, (22,30,40), sr, border_radius=4)
            pygame.draw.rect(s, _BORDER, sr, width=1, border_radius=4)
            lt = self._f_tiny.render(label, True, _TEXT)
            s.blit(lt, (sx+23-lt.get_width()//2, r.y+15)); sx += 52

    # ── Overlays ──────────────────────────────────────────────────────────
    def _render_overlay(self, name, tick):
        fn = {"gene_lab":self._overlay_gene_lab,"research":self._overlay_research,
              "stats":self._overlay_stats,"encyclopedia":self._overlay_encyclopedia}.get(name)
        if fn: fn(tick)

    def _overlay_bg(self, r, title):
        s = self.screen
        bg = pygame.Surface((r.width, r.height), pygame.SRCALPHA)
        bg.fill((12, 16, 22, 238)); s.blit(bg, r.topleft)
        pygame.draw.rect(s, _BORDER, r, width=1, border_radius=8)
        pygame.draw.line(s, _ACCENT, (r.x+8, r.y), (r.right-8, r.y), 2)
        tt = self._f_lg.render(title, True, _ACCENT)
        s.blit(tt, (r.x+16, r.y+10))
        cr = pygame.Rect(r.right-34, r.y+9, 24, 24)
        pygame.draw.rect(s, (40,18,18), cr, border_radius=4)
        pygame.draw.rect(s, _RED, cr, width=1, border_radius=4)
        ct = self._f_sm.render("✕", True, _RED)
        s.blit(ct, (cr.x+7, cr.y+5))
        mp = pygame.mouse.get_pos()
        if cr.collidepoint(mp) and pygame.mouse.get_pressed()[0]:
            self._active_overlay = None

    def _overlay_gene_lab(self, tick):
        s = self.screen
        w, h = 620, self._H - 110
        r = pygame.Rect(20, 54, w, h)
        self._overlay_bg(r, "🧬  Gene Lab — Species Creator")
        y = r.y + 50

        hdr = self._f_md.render("DESIGN YOUR SPECIES", True, _ACCENT)
        s.blit(hdr, (r.x+20, y)); y += 30

        genes = [
            ("Speed",        3.0, 0.1, 10.0, _ACCENT,  "Physical"),
            ("Size",         3.0, 0.1, 10.0, _ACCENT,  "Physical"),
            ("Strength",     3.0, 0.1, 10.0, _ACCENTB, "Physical"),
            ("Vision",       4.0, 1.0, 10.0, _ACCENTB, "Physical"),
            ("Intelligence", 3.0, 1.0, 10.0, _PURPLE,  "Behavioral"),
            ("Aggression",   3.0, 0.0, 10.0, _AMBER,   "Behavioral"),
            ("Camouflage",   2.0, 0.0, 10.0, _ACCENT,  "Physical"),
            ("Repro. Rate",  2.0, 0.1, 10.0, (255,100,200), "Genetic"),
            ("Mutation Rate",0.05,0.001,0.5, _PURPLE,  "Genetic"),
            ("Adaptability", 4.0, 0.0, 10.0, _ACCENTB, "Genetic"),
        ]
        cols = [(r.x+20,r.y+80),(r.x+330,r.y+80)]
        for i,(name,val,lo,hi,col,cat) in enumerate(genes):
            col_x = cols[i%2][0]; gy = y + (i//2)*60
            cat_t = self._f_tiny.render(cat.upper(), True, (60,70,85))
            s.blit(cat_t, (col_x, gy-2))
            self._draw_slider_inline(s, col_x, gy+12, 270, name, val, lo, hi, col)

        y = r.y + h - 130
        pygame.draw.line(s, _BORDER, (r.x+15, y), (r.right-15, y)); y += 14

        tl_lbl = self._f_sm.render("TROPHIC LEVEL:", True, _MUTED)
        s.blit(tl_lbl, (r.x+20, y))
        for i,(tl,col) in enumerate([("Herbivore",_ACCENT),("Omnivore",_AMBER),("Carnivore",_RED),("Apex",(220,0,80))]):
            tr = pygame.Rect(r.x+165+i*90, y-3, 82, 26)
            pygame.draw.rect(s, (22,30,22) if i==0 else (22,27,34), tr, border_radius=5)
            pygame.draw.rect(s, col, tr, width=1, border_radius=5)
            tt = self._f_tiny.render(tl, True, col)
            s.blit(tt, (tr.x+tr.w//2-tt.get_width()//2, tr.y+7))
        y += 38

        for i,(label,acc,bg2) in enumerate([("✦ CREATE SPECIES",_ACCENT,(0,55,35)),
                                             ("◈ SAVE TEMPLATE",_ACCENTB,(0,30,55)),
                                             ("⟳ RANDOM",_AMBER,(50,35,0))]):
            br = pygame.Rect(r.x+20+i*195, y, 180, 38)
            pygame.draw.rect(s, bg2, br, border_radius=6)
            pygame.draw.rect(s, acc, br, width=1, border_radius=6)
            bt = self._f_sm.render(label, True, _TEXT)
            s.blit(bt, (br.x+br.w//2-bt.get_width()//2, br.y+11))

    def _overlay_research(self, tick):
        s = self.screen
        r = pygame.Rect(40, 54, self._W-80, self._H-110)
        self._overlay_bg(r, "🔬  Research Tree")
        if not self.engine.research: return
        rp = int(self.engine.research.points)
        rp_t = self._f_md.render(f"Research Points: {rp} RP", True, _ACCENT)
        s.blit(rp_t, (r.x+16, r.y+44))

        nodes = self.engine.research.get_all_nodes()
        tier_y: dict = {}
        for node in nodes:
            tier = node.get("tier", 1)
            idx  = tier_y.get(tier, 0); tier_y[tier] = idx+1
            nx   = r.x + 20 + (tier-1)*190
            ny   = r.y + 80 + idx*72
            if ny > r.bottom - 60: continue
            if node["is_unlocked"]:  nc = _ACCENT
            elif node["is_available"] and node["can_afford"]: nc = _ACCENTB
            elif node["is_available"]: nc = _AMBER
            else: nc = _BORDER
            nr = pygame.Rect(nx, ny, 170, 58)
            bg2 = (14,24,18) if node["is_unlocked"] else (16,22,30)
            pygame.draw.rect(s, bg2, nr, border_radius=6)
            pygame.draw.rect(s, nc, nr, width=1+(1 if node["is_unlocked"] else 0), border_radius=6)
            nt = self._f_tiny.render(node.get("name","?")[:22], True, nc)
            ct2 = self._f_tiny.render(f"{node.get('cost',0)} RP", True, _MUTED)
            s.blit(nt, (nx+8, ny+8)); s.blit(ct2, (nx+8, ny+28))
            if node["is_unlocked"]:
                ck = self._f_sm.render("✓", True, _ACCENT); s.blit(ck, (nx+148, ny+8))
            mp = pygame.mouse.get_pos()
            if nr.collidepoint(mp) and node["is_available"] and node["can_afford"] and pygame.mouse.get_pressed()[0]:
                self.engine.research.unlock(node["node_id"])

        tier_labels = {1:"Foundation",2:"Applied Biology",3:"Env. Engineering",4:"Advanced Sim",5:"Mastery"}
        for tier,label in tier_labels.items():
            tx = r.x+20+(tier-1)*190
            lt = self._f_tiny.render(label, True, (60,70,85))
            s.blit(lt,(tx, r.y+60))
            pygame.draw.line(s,_BORDER,(tx,r.y+70),(tx,r.bottom-10))

    def _overlay_stats(self, tick):
        s = self.screen
        r = pygame.Rect(40, 54, self._W-80, self._H-110)
        self._overlay_bg(r, "📊  Statistics Dashboard")
        if not self.engine.statistics: return
        snap = self.engine.statistics.last_snapshot or {}

        metrics = [
            ("Total Population",    f"{snap.get('total_population',0):,}",         _TEXT),
            ("Active Species",       str(snap.get('species_count',0)),              _ACCENTB),
            ("Biodiversity Index",   f"{snap.get('biodiversity',0.0):.3f}",         _ACCENT),
            ("Evolution Events",     str(snap.get('evolution_events',0)),           _ACCENTB),
            ("Extinction Events",    str(snap.get('extinction_events',0)),          _RED),
            ("Speciation Events",    str(snap.get('speciation_events',0)),          _PURPLE),
            ("Predation Events",     str(snap.get('predation_events',0)),           _AMBER),
            ("World Tick",           str(tick),                                     _MUTED),
        ]
        y = r.y+52
        for i,(lbl,val,col) in enumerate(metrics):
            col_x = r.x+30 + (i%2)*340; row_y = y + (i//2)*40
            lt = self._f_sm.render(lbl+":", True, _MUTED)
            vt = self._f_md.render(str(val), True, col)
            s.blit(lt,(col_x,row_y)); s.blit(vt,(col_x+200,row_y))

        # Population graph
        ph = list(self.engine.statistics.population_history)
        if len(ph) >= 2:
            gy = r.y+230; gx = r.x+30; gw = r.width-60; gh = 130
            gr2 = pygame.Rect(gx,gy,gw,gh)
            pygame.draw.rect(s,(14,20,28),gr2,border_radius=4)
            pygame.draw.rect(s,_BORDER,gr2,width=1,border_radius=4)
            lt = self._f_sm.render("Population History", True, _MUTED)
            s.blit(lt,(gx+8,gy+4))
            vals = [p for _,p in ph]; max_v = max(vals) or 1
            pts  = []
            for i,v in enumerate(vals):
                px2 = gx+4+int(i/max(1,len(vals)-1)*(gw-8))
                py2 = gy+gh-18-int(v/max_v*(gh-26))
                pts.append((px2,py2))
            if len(pts)>=2: pygame.draw.lines(s,_ACCENT,False,pts,2)
            # Biodiversity
            bh2 = list(self.engine.statistics.biodiversity_history)
            if len(bh2)>=2:
                gy2=gy+gh+18; gr3=pygame.Rect(gx,gy2,gw,80)
                pygame.draw.rect(s,(14,20,28),gr3,border_radius=4)
                pygame.draw.rect(s,_BORDER,gr3,width=1,border_radius=4)
                lt2=self._f_sm.render("Biodiversity Index",True,_MUTED); s.blit(lt2,(gx+8,gy2+4))
                bvals=[b for _,b in bh2]; bmax=max(bvals) or 1
                bpts=[(gx+4+int(i/max(1,len(bvals)-1)*(gw-8)),gy2+70-int(v/bmax*60)) for i,v in enumerate(bvals)]
                if len(bpts)>=2: pygame.draw.lines(s,_PURPLE,False,bpts,2)

    def _overlay_encyclopedia(self, tick):
        s = self.screen
        r = pygame.Rect(40, 54, self._W-80, self._H-110)
        self._overlay_bg(r, "📖  Species Encyclopedia")
        if not self.engine.species_registry: return

        y = r.y+52
        old_clip = s.get_clip()
        s.set_clip(pygame.Rect(r.x,y,r.width,r.bottom-y-8))

        all_sp = self.engine.species_registry.all()
        living = [sp for sp in all_sp if not sp.is_extinct()]
        extinct = [sp for sp in all_sp if sp.is_extinct()]

        for sp in living + extinct:
            if y > r.bottom - 30: break
            col  = sp.color
            stat = "EXTINCT" if sp.is_extinct() else "ALIVE"
            scol = _RED if sp.is_extinct() else _ACCENT
            pygame.draw.circle(s, col, (r.x+20, y+12), 7)
            nt = self._f_sm.render(sp.name[:24], True, _MUTED if sp.is_extinct() else _TEXT)
            st = self._f_tiny.render(stat, True, scol)
            pt = self._f_tiny.render(
                f"Pop: {sp.population}  Gen: {sp.generation}  {sp.trophic_label}  Biome: {', '.join(sp.biomes[:2])}", True, _MUTED)
            s.blit(nt,(r.x+35,y)); s.blit(st,(r.right-90,y)); s.blit(pt,(r.x+35,y+17))
            pygame.draw.line(s,_BORDER,(r.x+10,y+37),(r.right-10,y+37))
            y += 42

        s.set_clip(old_clip)

    # ── Slider helper ─────────────────────────────────────────────────────
    def _draw_slider_inline(self,s,x,y,w,label,val,lo,hi,color):
        lt = self._f_tiny.render(label, True, _MUTED)
        s.blit(lt, (x, y))
        vt = self._f_tiny.render(f"{val:.2f}" if val<1 else f"{val:.1f}", True, color)
        s.blit(vt, (x+w-vt.get_width(), y))
        tr = pygame.Rect(x, y+16, w, 5)
        pygame.draw.rect(s, (40,50,65), tr, border_radius=3)
        ratio = (val-lo)/max(0.001,hi-lo)
        fw = int(ratio*w)
        if fw>0: pygame.draw.rect(s, color, pygame.Rect(x,y+16,fw,5), border_radius=3)
        pygame.draw.circle(s, color, (x+fw, y+18), 7)

    # ── Button helper ─────────────────────────────────────────────────────
    def _btn_handle(self,btn,event):
        if event.type==pygame.MOUSEBUTTONUP and event.button==1:
            if btn["rect"].collidepoint(event.pos):
                self._toggle_overlay(btn["action"])

    def _toggle_overlay(self,name):
        if self._active_overlay==name: self._active_overlay=None
        else: self._active_overlay=name
        if self.engine.audio: self.engine.audio.play_ui("click")

    # ── Notifications ─────────────────────────────────────────────────────
    def _render_notifications(self):
        self._notifications=[n for n in self._notifications if n["timer"]>0]
        for i,n in enumerate(self._notifications[-4:]):
            n["timer"]-=1
            alpha=min(255,n["timer"]*6)
            ns=pygame.Surface((370,34),pygame.SRCALPHA)
            ns.fill((*n["bg"],min(210,alpha)))
            pygame.draw.rect(ns,(*n["color"],alpha),ns.get_rect(),width=1,border_radius=5)
            txt=self._f_sm.render(n["text"][:46],True,(*n["color"],alpha))
            ns.blit(txt,(10,9))
            self.screen.blit(ns,(self._W//2-185,50+i*40))

    def _push(self,text,color=_ACCENT,bg=(14,20,28)):
        self._notifications.append({"text":text,"color":color,"bg":bg,"timer":self._notif_duration})

    def _on_achievement(self,e): self._push(f"🏆 Achievement: {e.data.get('name','')}", _AMBER,(28,22,8))
    def _on_disaster(self,e):    self._push(f"⚠ {e.data.get('type','').replace('_',' ').title()} Event!", _RED,(28,10,10))
    def _on_extinct(self,e):     self._push(f"💀 {e.data.get('name','')} has gone extinct.", _RED)
    def _on_adaptation(self,e):
        sp=self.engine.species_registry.get(e.data.get("species_id","")) if self.engine.species_registry else None
        name=sp.name if sp else "Species"
        self._push(f"🧬 {name} adapting: {e.data.get('gene','trait')}", _ACCENTB)
    def _on_speciation(self,e):  self._push(f"✦ New species: {e.data.get('child_name','')}", _PURPLE)
    def _on_research(self,e):    self._push(f"🔬 Unlocked: {e.data.get('name','Research')}", _ACCENTB)

    # ── Menu Actions ──────────────────────────────────────────────────────
    def _menu_action(self,action):
        from engine.game_engine import GameState
        if action=="quit":
            self.bus.publish("engine:quit",{})
        elif action in ("sandbox","campaign"):
            self.bus.publish("engine:change_state",{"state":"PLAYING"})
            if self.engine.world: self.engine.world.generate()
            if self.engine.audio: self.engine.audio.play_music("ecosystem_ambient")
            # Seed starter species for sandbox
            if action=="sandbox": self._seed_starter_species()
        elif action=="load":
            pass  # Save screen handled by bottom bar

    def _seed_starter_species(self):
        """Add two starter species to make the world feel alive immediately."""
        if not (self.engine.species_registry and self.engine.world and self.engine.world.tiles):
            return
        from genetics.genome import Genome
        from species.species import Species
        from utils.color_utils import species_color

        # Herbivore
        g1=Genome(); g1.physical.speed=5.0; g1.physical.size=2.5; g1.behavioral.fearfulness=7.0; g1.behavioral.social_behavior=7.0
        sp1=self.engine.species_registry.create_and_register("Meadow Grazer",2,g1,["grassland"],created_tick=0)
        tile=self.engine.world.random_tile_in_biome("grassland") or self.engine.world.random_passable_tile()
        if tile:
            for _ in range(15): sp1.spawn_creature(tile.grid_x,tile.grid_y,0)

        # Predator
        g2=Genome(); g2.physical.speed=7.0; g2.physical.strength=6.0; g2.behavioral.aggression=7.0; g2.behavioral.fearfulness=2.0
        sp2=self.engine.species_registry.create_and_register("Grassland Hunter",3,g2,["grassland"],created_tick=0)
        tile2=self.engine.world.random_tile_in_biome("grassland") or self.engine.world.random_passable_tile()
        if tile2:
            for _ in range(6): sp2.spawn_creature(tile2.grid_x,tile2.grid_y,0)
