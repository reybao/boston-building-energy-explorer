// Plain-language labels only. Analytical ratios and eligibility stay unchanged.
export function comparisonText(ratio){
  if(!Number.isFinite(ratio))return 'Comparison unavailable';
  const difference=Math.abs((ratio-1)*100);
  if(difference<.5)return 'About the same';
  return `${Math.round(difference).toLocaleString('en-US')}% ${ratio>1?'higher':'lower'}`;
}
export function comparisonSentence(ratio){
  const label=comparisonText(ratio);
  if(!Number.isFinite(ratio))return label;
  return label+(label==='About the same'?' as':' than')+' similar buildings';
}
