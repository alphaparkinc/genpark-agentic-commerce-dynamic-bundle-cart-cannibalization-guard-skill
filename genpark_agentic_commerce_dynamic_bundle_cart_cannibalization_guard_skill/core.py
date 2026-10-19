# -*- coding: utf-8 -*-
"""Dynamic Bundle Cart Cannibalization Guard Skill for GenPark Agentic Commerce."""
import json
from typing import Dict, Any

def evaluate_bundle_profitability_and_cannibalization(primary_item_price_usd: float, primary_item_margin_pct: float, bundled_addon_price_usd: float, bundled_addon_margin_pct: float, proposed_bundle_discount_pct: float) -> Dict[str, Any]:
    standalone_gross_revenue = primary_item_price_usd + bundled_addon_price_usd
    standalone_gross_margin = (primary_item_price_usd * (primary_item_margin_pct / 100.0)) + (bundled_addon_price_usd * (bundled_addon_margin_pct / 100.0))

    bundle_discount_amount = standalone_gross_revenue * (proposed_bundle_discount_pct / 100.0)
    net_bundle_revenue = standalone_gross_revenue - bundle_discount_amount
    net_bundle_profit = standalone_gross_margin - bundle_discount_amount
    blended_margin_pct = (net_bundle_profit / net_bundle_revenue) * 100.0 if net_bundle_revenue > 0 else 0.0

    # Cannibalization rule: Net profit in dollar terms must exceed primary item alone by at least 15%
    primary_standalone_profit = primary_item_price_usd * (primary_item_margin_pct / 100.0)
    profit_lift_usd = net_bundle_profit - primary_standalone_profit
    
    is_cannibalizing = profit_lift_usd < (primary_standalone_profit * 0.15)
    margin_floor_breached = blended_margin_pct < 25.0

    if is_cannibalizing or margin_floor_breached:
        verdict = "REJECT_EXCESSIVE_DISCOUNT"
        recommended_safe_discount = round(min(12.0, (standalone_gross_margin - (primary_standalone_profit * 1.2)) / standalone_gross_revenue * 100.0), 1)
    else:
        verdict = "APPROVE_BUNDLE"
        recommended_safe_discount = proposed_bundle_discount_pct

    return {
        "standalone_sum_usd": round(standalone_gross_revenue, 2),
        "standalone_combined_profit_usd": round(standalone_gross_margin, 2),
        "net_bundle_revenue_usd": round(net_bundle_revenue, 2),
        "net_bundle_profit_usd": round(net_bundle_profit, 2),
        "blended_margin_pct": round(blended_margin_pct, 1),
        "profit_lift_over_single_item_usd": round(profit_lift_usd, 2),
        "cannibalization_risk": is_cannibalizing,
        "bundle_policy_decision": verdict,
        "approved_discount_pct": max(5.0, recommended_safe_discount),
        "guardrail": "GenPark Commerce Margin Integrity Engine"
    }

def synthesize_personalized_bundle_offer(bundle_title: str, primary_item_name: str, addon_item_name: str, approved_discount_pct: float, net_bundle_price_usd: float) -> Dict[str, Any]:
    copy_text = (
        f"Unlock the '{bundle_title}': Pair your {primary_item_name} with {addon_item_name} "
        f"and instantly save {approved_discount_pct}% on the combined set. "
        f"Complete bundle bundle price: ${net_bundle_price_usd:.2f}."
    )

    return {
        "title": bundle_title,
        "headline_copy": f"Save {approved_discount_pct}%: Complete Your Setup",
        "promotional_copy": copy_text,
        "bundle_price_usd": net_bundle_price_usd,
        "cta_button_text": f"Add Both to Cart (${net_bundle_price_usd:.2f})",
        "direct_bundle_cart_url": f"https://checkout.genpark.ai/bundle/add?sku_a={primary_item_name.lower().replace(' ', '-')}&sku_b={addon_item_name.lower().replace(' ', '-')}&disc={approved_discount_pct}"
    }
