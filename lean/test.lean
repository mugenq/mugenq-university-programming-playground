import init.data.nat
open classical

theorem and_commutative (p q : Prop) : p ∧ q → q ∧ p :=
begin
assume Hpq : p ∧ q,
have Hp : p, from and.elim_left Hpq,
have Hq : q, from and.elim_right Hpq,
show q ∧ p, from and.intro Hq Hp
end



theorem or_commutative (p q : Prop) : p ∨ q → q ∨ p :=
begin
assume Hpq : p ∨ q,
Hpq.elim
(assume hp : p, or.inr hp)
(assume hq : q, or.inl hq)
end

variables p q r : Prop

-- distributivity
example : p ∧ (q ∨ r) ↔ (p ∧ q) ∨ (p ∧ r) :=
iff.intro
  (assume h : p ∧ (q ∨ r),
    have hp : p, from h.left,
    or.elim (h.right)
      (assume hq : q,
        show (p ∧ q) ∨ (p ∧ r), from or.inl ⟨hp, hq⟩)
      (assume hr : r,
        show (p ∧ q) ∨ (p ∧ r), from or.inr ⟨hp, hr⟩))
  (assume h : (p ∧ q) ∨ (p ∧ r),
    or.elim h
      (assume hpq : p ∧ q,
        have hp : p, from hpq.left,
        have hq : q, from hpq.right,
        show p ∧ (q ∨ r), from ⟨hp, or.inl hq⟩)
      (assume hpr : p ∧ r,
        have hp : p, from hpr.left,
        have hr : r, from hpr.right,
        show p ∧ (q ∨ r), from ⟨hp, or.inr hr⟩))

-- an example that requires classical reasoning
example : ¬(p ∧ ¬q) → (p → q) :=
assume h : ¬(p ∧ ¬q),
assume hp : p,
show q, from
  or.elim (em q)
    (assume hq : q, hq)
    (assume hnq : ¬q, absurd (and.intro hp hnq) h)