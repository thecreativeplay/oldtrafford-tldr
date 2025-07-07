import { useEffect } from 'react';

const TwitterSidebar = () => {
  useEffect(() => {
    const script = document.createElement('script');
    script.src = 'https://platform.twitter.com/widgets.js';
    script.async = true;
    document.body.appendChild(script);
  }, []);

  return (
    <div id="twitter-sidebar" className="fixed top-20 right-0 w-[300px] max-h-[90vh] overflow-y-auto bg-white border-l border-gray-300 p-4 z-50">
      <h3 className="text-lg font-semibold mb-2">🔁 Transfer Alerts</h3>

      <a
        className="twitter-timeline"
        data-chrome="noheader nofooter noborders transparent"
        data-tweet-limit="5"
        href="https://twitter.com/FabrizioRomano?ref_src=twsrc%5Etfw"
      >
        Tweets by FabrizioRomano
      </a>

      <a
        className="twitter-timeline"
        data-chrome="noheader nofooter noborders transparent"
        data-tweet-limit="5"
        href="https://twitter.com/David_Ornstein?ref_src=twsrc%5Etfw"
      >
        Tweets by David_Ornstein
      </a>
    </div>
  );
};

export default TwitterSidebar;
