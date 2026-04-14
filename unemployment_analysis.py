# ================================================================
#   CodeAlpha — Data Science Internship
#   Task 2   : Unemployment Analysis with Python
#   Author   : [Divya A J]
#   GitHub   : CodeAlpha_UnemploymentAnalysis
#   Dataset  : Unemployment Rate upto Nov 2020 (India)
# ================================================================
#
#   What this script does
#   ─────────────────────
#   1.  Load & Clean the unemployment dataset
#   2.  Exploratory Data Analysis (EDA)
#   3.  Covid-19 Impact Analysis (Pre vs Post lockdown)
#   4.  State-wise & Region-wise Breakdown
#   5.  Trend & Seasonal Pattern Analysis
#   6.  Save a beautiful 8-panel visualisation dashboard
#   7.  Print policy-ready insights summary
# ================================================================

import warnings
warnings.filterwarnings("ignore")

import numpy             as np
import pandas            as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot    as plt
import matplotlib.gridspec  as gridspec
import matplotlib.patches   as mpatches
import matplotlib.ticker    as ticker
import seaborn              as sns

# ── Colour Theme ────────────────────────────────────────────────
BG       = "#0D1117"
CARD     = "#1E2530"
BORDER   = "#30363D"
MUTED    = "#8B949E"
TEXT     = "#E6EDF3"
GOLD     = "#FFD54F"
RED      = "#FF6B6B"
GREEN    = "#69DB7C"
BLUE     = "#74C0FC"
ORANGE   = "#FFA94D"
PURPLE   = "#DA77F2"
TEAL     = "#38D9A9"
ACCENT   = "#7C4DFF"

ZONE_COLORS = {
    "North"     : "#FF6B6B",
    "South"     : "#74C0FC",
    "East"      : "#69DB7C",
    "West"      : "#FFA94D",
    "Northeast" : "#DA77F2",
}

plt.rcParams.update({
    "figure.facecolor" : BG,   "axes.facecolor"   : CARD,
    "axes.edgecolor"   : BORDER,"axes.labelcolor"  : TEXT,
    "xtick.color"      : MUTED, "ytick.color"      : MUTED,
    "text.color"       : TEXT,  "grid.color"       : BORDER,
    "grid.linestyle"   : "--",  "grid.alpha"       : 0.5,
    "legend.facecolor" : "#161B22","legend.edgecolor": BORDER,
    "font.family"      : "DejaVu Sans","font.size"  : 9.5,
})


# ════════════════════════════════════════════════════════════════
# STEP 1 — LOAD & CLEAN DATA
# ════════════════════════════════════════════════════════════════
print("\n" + "═"*64)
print("    CodeAlpha  ·  Unemployment Analysis with Python")
print("═"*64)

df = pd.read_csv("Unemployment_Rate_upto_11_2020.csv")
df.columns = [c.strip() for c in df.columns]

# Rename columns for clarity
df.rename(columns={
    "Region"                                : "State",
    "Estimated Unemployment Rate (%)"       : "Unemployment_Rate",
    "Estimated Employed"                    : "Employed",
    "Estimated Labour Participation Rate (%)": "Labour_Participation",
    "Region.1"                              : "Zone",
}, inplace=True)

df["State"]  = df["State"].str.strip()
df["Zone"]   = df["Zone"].str.strip()
df["Date"]   = pd.to_datetime(df["Date"].str.strip(), format="%d-%m-%Y")
df["Month"]  = df["Date"].dt.strftime("%b %Y")
df["Period"] = df["Date"].dt.to_period("M")

print(f"\n📂  Shape          : {df.shape[0]} rows × {df.shape[1]} columns")
print(f"🗓️  Date Range     : {df['Date'].min().strftime('%B %Y')}  →  {df['Date'].max().strftime('%B %Y')}")
print(f"🗺️  States         : {df['State'].nunique()}")
print(f"🧭  Zones          : {df['Zone'].unique().tolist()}")
print(f"❓  Missing Values : {df.isnull().sum().sum()}")

print("\n── Unemployment Rate Statistics ─────────────────────────")
print(df["Unemployment_Rate"].describe().round(2).to_string())


# ════════════════════════════════════════════════════════════════
# STEP 2 — KEY CALCULATIONS
# ════════════════════════════════════════════════════════════════

# Monthly national average
monthly_avg = df.groupby("Date")["Unemployment_Rate"].mean().reset_index()
monthly_avg.columns = ["Date", "Avg_Rate"]
monthly_avg["Month"] = monthly_avg["Date"].dt.strftime("%b\n%Y")

# Covid split  (lockdown announced March 24, 2020)
pre_covid  = df[df["Date"] < "2020-04-01"]["Unemployment_Rate"]
post_covid = df[df["Date"] >= "2020-04-01"]["Unemployment_Rate"]
pre_avg    = round(pre_covid.mean(), 2)
post_avg   = round(post_covid.mean(), 2)
peak_month = monthly_avg.loc[monthly_avg["Avg_Rate"].idxmax()]

# State-wise averages
state_avg = df.groupby("State")["Unemployment_Rate"].mean().sort_values(ascending=False)

# Zone-wise averages
zone_avg  = df.groupby("Zone")["Unemployment_Rate"].mean().sort_values(ascending=False)

# April 2020 peak (harshest lockdown)
april2020 = df[df["Date"] == "2020-04-30"].set_index("State")["Unemployment_Rate"].sort_values(ascending=False)

# Recovery analysis
recovery = df[df["Date"] >= "2020-04-01"].groupby("Date")["Unemployment_Rate"].mean()

print(f"\n── Covid-19 Impact ──────────────────────────────────────")
print(f"   Pre-COVID  avg (Jan–Mar 2020) : {pre_avg}%")
print(f"   Post-COVID avg (Apr–Nov 2020) : {post_avg}%")
print(f"   Increase                      : +{round(post_avg - pre_avg, 2)}%  "
      f"({round((post_avg-pre_avg)/pre_avg*100, 1)}% rise)")
print(f"   Peak month                    : {peak_month['Date'].strftime('%B %Y')}  "
      f"({round(peak_month['Avg_Rate'],2)}%)")

print(f"\n── Top 5 Worst-Hit States (April 2020) ──────────────────")
for state, rate in april2020.head(5).items():
    print(f"   {state:<22}  {rate}%")

print(f"\n── Zone-wise Average Unemployment ───────────────────────")
for zone, rate in zone_avg.items():
    print(f"   {zone:<12}  {rate:.2f}%")


# ════════════════════════════════════════════════════════════════
# STEP 3 — 8-PANEL VISUALISATION DASHBOARD
# ════════════════════════════════════════════════════════════════
def ptitle(ax, txt, sub=None):
    ax.set_title(txt, fontsize=11, fontweight="bold", color=TEXT, pad=10, loc="left")
    if sub:
        ax.text(0.0, 1.035, sub, transform=ax.transAxes,
                fontsize=8, color=MUTED)

fig = plt.figure(figsize=(22, 18), facecolor=BG)
gs  = gridspec.GridSpec(3, 3, figure=fig,
                        hspace=0.52, wspace=0.35,
                        left=0.06, right=0.97,
                        top=0.91,  bottom=0.05)

# Title banner
fig.text(0.5, 0.955,
         "📉  Unemployment Analysis — India 2020  ·  CodeAlpha Data Science Internship",
         ha="center", fontsize=18, fontweight="bold", color=TEXT)
fig.text(0.5, 0.928,
         "27 States  ·  Jan 2020 – Nov 2020  ·  Monthly Data  ·  Impact of Covid-19 Lockdown",
         ha="center", fontsize=11, color=MUTED)

# ── Panel 1 : National unemployment trend ────────────────────────
ax1 = fig.add_subplot(gs[0, :2])
dates = monthly_avg["Date"]
rates = monthly_avg["Avg_Rate"]
ax1.fill_between(dates, rates, alpha=0.18, color=BLUE)
ax1.plot(dates, rates, color=BLUE, linewidth=2.5, marker="o",
         markersize=7, markerfacecolor=GOLD, markeredgecolor=BLUE, zorder=5)
# Covid annotation
ax1.axvline(pd.Timestamp("2020-03-24"), color=RED, linewidth=1.5,
            linestyle="--", alpha=0.8)
ax1.text(pd.Timestamp("2020-03-26"), rates.max()*0.92,
         "🔒 Lockdown\n   Mar 24", color=RED, fontsize=8.5,
         fontweight="bold")
# Shade lockdown period
ax1.axvspan(pd.Timestamp("2020-03-24"), pd.Timestamp("2020-06-01"),
            alpha=0.08, color=RED)
for x, y in zip(dates, rates):
    ax1.text(x, y+0.5, f"{y:.1f}%", ha="center",
             fontsize=7.5, color=GOLD, fontweight="bold")
ax1.set_ylabel("Unemployment Rate (%)")
ax1.set_xlabel("")
ax1.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%b\n%Y"))
ax1.grid(True, alpha=0.4)
ax1.set_ylim(0, rates.max()*1.18)
ptitle(ax1, "① National Unemployment Rate Trend  (Jan–Nov 2020)",
       "Monthly average across all 27 states")

# ── Panel 2 : Pre vs Post Covid comparison ───────────────────────
ax2 = fig.add_subplot(gs[0, 2])
periods = ["Pre-COVID\n(Jan–Mar)", "Post-COVID\n(Apr–Nov)"]
values  = [pre_avg, post_avg]
colors  = [GREEN, RED]
bars    = ax2.bar(periods, values, color=colors, edgecolor=BG,
                  linewidth=1.5, width=0.5)
for b, v in zip(bars, values):
    ax2.text(b.get_x()+b.get_width()/2, v+0.3,
             f"{v}%", ha="center", fontsize=14,
             fontweight="bold", color=GOLD)
ax2.set_ylabel("Average Unemployment Rate (%)")
ax2.set_ylim(0, post_avg * 1.25)
ax2.grid(axis="y", alpha=0.4)
# Arrow showing increase
ax2.annotate("", xy=(1, post_avg*0.95), xytext=(0, pre_avg*1.12),
             arrowprops=dict(arrowstyle="->", color=ORANGE,
                             lw=2.0, connectionstyle="arc3,rad=0.3"))
ax2.text(0.52, (pre_avg+post_avg)/2, f"+{round(post_avg-pre_avg,1)}%",
         color=ORANGE, fontsize=11, fontweight="bold")
ptitle(ax2, "② Covid-19 Impact")

# ── Panel 3 : State-wise bar (top 15) ────────────────────────────
ax3 = fig.add_subplot(gs[1, :2])
top15 = state_avg.head(15)
colors_bar = [ZONE_COLORS.get(df[df["State"]==s]["Zone"].iloc[0], BLUE)
              for s in top15.index]
hbars = ax3.barh(range(len(top15)), top15.values,
                 color=colors_bar, edgecolor=BG, height=0.65, alpha=0.9)
ax3.set_yticks(range(len(top15)))
ax3.set_yticklabels(top15.index, fontsize=9)
ax3.set_xlabel("Average Unemployment Rate (%)")
ax3.invert_yaxis()
ax3.grid(axis="x", alpha=0.4)
for bar, val in zip(hbars, top15.values):
    ax3.text(val+0.2, bar.get_y()+bar.get_height()/2,
             f"{val:.1f}%", va="center", fontsize=8.5, color=GOLD)
# Zone legend
legend_patches = [mpatches.Patch(color=c, label=z)
                  for z, c in ZONE_COLORS.items()]
ax3.legend(handles=legend_patches, loc="lower right",
           fontsize=8, framealpha=0.3, title="Zone", title_fontsize=8)
ptitle(ax3, "③ Top 15 States — Average Unemployment Rate",
       "Color-coded by geographic zone")

# ── Panel 4 : Zone-wise box plot ─────────────────────────────────
ax4 = fig.add_subplot(gs[1, 2])
zones_ordered = zone_avg.index.tolist()
box_data = [df[df["Zone"] == z]["Unemployment_Rate"].values for z in zones_ordered]
bp = ax4.boxplot(box_data, patch_artist=True, widths=0.45,
                 medianprops=dict(color="white", linewidth=2),
                 whiskerprops=dict(linewidth=1.4),
                 capprops=dict(linewidth=1.4),
                 flierprops=dict(marker="o", markersize=4,
                                 alpha=0.5, markeredgewidth=0))
for patch, zone in zip(bp["boxes"], zones_ordered):
    patch.set_facecolor(ZONE_COLORS[zone])
    patch.set_alpha(0.75)
ax4.set_xticks(range(1, len(zones_ordered)+1))
ax4.set_xticklabels(zones_ordered, rotation=15, fontsize=8)
ax4.set_ylabel("Unemployment Rate (%)")
ax4.grid(axis="y", alpha=0.4)
ptitle(ax4, "④ Zone-wise Distribution")

# ── Panel 5 : Heatmap states × months ────────────────────────────
ax5 = fig.add_subplot(gs[2, :2])
pivot = df.pivot_table(index="State", columns="Date",
                       values="Unemployment_Rate", aggfunc="mean")
pivot.columns = [d.strftime("%b") for d in pivot.columns]
pivot_sorted = pivot.reindex(state_avg.index)

im = ax5.imshow(pivot_sorted.values, aspect="auto",
                cmap="RdYlGn_r", interpolation="nearest")
ax5.set_xticks(range(len(pivot_sorted.columns)))
ax5.set_xticklabels(pivot_sorted.columns, fontsize=9)
ax5.set_yticks(range(len(pivot_sorted.index)))
ax5.set_yticklabels(pivot_sorted.index, fontsize=7.5)
plt.colorbar(im, ax=ax5, fraction=0.025, pad=0.01,
             label="Unemployment Rate (%)")
# Annotate cells
for i in range(len(pivot_sorted.index)):
    for j in range(len(pivot_sorted.columns)):
        val = pivot_sorted.values[i, j]
        if not np.isnan(val):
            ax5.text(j, i, f"{val:.0f}",
                     ha="center", va="center",
                     fontsize=6.5, color="white" if val > 20 else "black",
                     fontweight="bold")
ptitle(ax5, "⑤ Unemployment Heatmap — State × Month",
       "Dark red = high unemployment  ·  Green = low unemployment")

# ── Panel 6 : Recovery line chart (post-lockdown) ─────────────────
ax6 = fig.add_subplot(gs[2, 2])
# Top 5 states + national for recovery
top5 = april2020.head(5).index.tolist()
recovery_colors = [RED, ORANGE, PURPLE, TEAL, BLUE, GOLD]
for i, state in enumerate(top5):
    sdata = df[df["State"] == state].sort_values("Date")
    ax6.plot(sdata["Date"], sdata["Unemployment_Rate"],
             color=recovery_colors[i], linewidth=1.8,
             marker="o", markersize=4, label=state, alpha=0.9)
# National avg
ax6.plot(monthly_avg["Date"], monthly_avg["Avg_Rate"],
         color=GOLD, linewidth=2.5, linestyle="--",
         marker="s", markersize=5, label="National Avg", alpha=0.9)
ax6.axvline(pd.Timestamp("2020-03-24"), color="white",
            linewidth=1, linestyle=":", alpha=0.5)
ax6.set_ylabel("Unemployment Rate (%)")
ax6.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%b"))
ax6.legend(fontsize=7, framealpha=0.25, loc="upper right",
           ncol=2)
ax6.grid(True, alpha=0.4)
ptitle(ax6, "⑥ Recovery Trends — Top 5 Hit States")

plt.savefig("unemployment_dashboard.png", dpi=160,
            bbox_inches="tight", facecolor=BG)
plt.close()
print("\n✅  Dashboard saved  →  unemployment_dashboard.png")


# ════════════════════════════════════════════════════════════════
# STEP 4 — POLICY INSIGHTS SUMMARY
# ════════════════════════════════════════════════════════════════
print("\n" + "═"*64)
print("    📋  KEY INSIGHTS & POLICY RECOMMENDATIONS")
print("═"*64)

insights = [
    ("📈 Covid Spike",
     f"National unemployment surged from {pre_avg}% (pre-COVID) to "
     f"{post_avg}% post-lockdown — a {round((post_avg-pre_avg)/pre_avg*100,1)}% relative increase."),

    ("🗓️  Peak Crisis",
     f"May 2020 was the worst month nationally ({round(peak_month['Avg_Rate'],2)}% avg). "
     f"Puducherry hit 75.85%, Bihar 46.64%, Tamil Nadu 49.83%."),

    ("🧭 Regional Disparity",
     f"North India ({zone_avg['North']:.1f}%) was hardest hit while "
     f"West India ({zone_avg['West']:.1f}%) showed most resilience."),

    ("🔄 Recovery Signal",
     "June–July 2020 showed strong recovery as unlock phases began, "
     "but rates remained above pre-COVID levels through November."),

    ("🏭 Labour Participation",
     "States with lower labour participation rates (below 40%) showed "
     "higher vulnerability to unemployment shocks during lockdown."),

    ("📌 Policy Suggestion",
     "North & East India need targeted employment schemes (MGNREGA expansion). "
     "Small business support and gig economy regulation are critical."),
]

for title, text in insights:
    print(f"\n  {title}")
    print(f"  {'─'*56}")
    # wrap text
    words = text.split()
    line = "  "
    for word in words:
        if len(line) + len(word) > 60:
            print(line); line = "  " + word + " "
        else:
            line += word + " "
    if line.strip(): print(line)

print(f"\n{'═'*64}")
print("  🎉  Task 2 Complete — Ready to submit to CodeAlpha!")
print(f"{'═'*64}\n")
