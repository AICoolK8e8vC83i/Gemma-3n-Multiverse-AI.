import React, { useState, useEffect, useRef } from 'react';
import {
  StyleSheet,
  Text,
  View,
  ScrollView,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
  RefreshControl,
  Dimensions,
  Animated,
  TextInput,
  Modal,
  FlatList,
} from 'react-native';
// Using simple React Native styling instead of complex animations
import AsyncStorage from '@react-native-async-storage/async-storage';
import { AGENT_EXPERTS, getAgentSuggestions, getRandomAgent } from './agentExperts';

const NeuralNet = () => {
  return (
    <View style={styles.neuralNet}>
      <Text style={styles.neuralText}>🧠⚡🔮✨</Text>
    </View>
  );
};

const SpaceBackground = () => {
  const universeEmojis = ['🌌', '⭐', '🌟', '✨', '💫', '🌠', '🪐', '🌙', '☄️', '🌈'];
  
  const elements = [...Array(15)].map((_, index) => (
    <Text
      key={index}
      style={[
        styles.spaceEmoji,
        {
          left: `${Math.random() * 90}%`,
          top: `${Math.random() * 90}%`,
          fontSize: Math.random() * 20 + 15,
        },
      ]}
    >
      {universeEmojis[Math.floor(Math.random() * universeEmojis.length)]}
    </Text>
  ));

  return <View style={styles.spaceContainer}>{elements}</View>;
};

export default function App() {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [lastCheck, setLastCheck] = useState(null);
  const [syncServerUrl, setSyncServerUrl] = useState('http://192.168.1.40:8000');
  const [apiKey, setApiKey] = useState('AIzaSyCDOdmCOy3YnkipnO0gJoQZ9KzjA7W59Ck');
  const [isPolling, setIsPolling] = useState(false);
  const [selectedAgent, setSelectedAgent] = useState(null);
  const [agentSuggestions, setAgentSuggestions] = useState([]);
  const [showAgentModal, setShowAgentModal] = useState(false);
  const [chatInput, setChatInput] = useState('');
  const pollingInterval = useRef(null);

  // Initialize app
  useEffect(() => {
    startPolling();
    return () => stopPolling();
  }, []);

  // Settings are now hardcoded in state

  const startPolling = () => {
    if (!syncServerUrl || !apiKey) return;
    
    setIsPolling(true);
    checkForNewMessages();
    
    // Poll every 30 seconds
    pollingInterval.current = setInterval(() => {
      checkForNewMessages();
    }, 30000);
  };

  const stopPolling = () => {
    setIsPolling(false);
    if (pollingInterval.current) {
      clearInterval(pollingInterval.current);
      pollingInterval.current = null;
    }
  };

  const checkForNewMessages = async () => {
    if (!syncServerUrl || !apiKey) return;
    
    setLoading(true);
    try {
      const pendingMessages = await getPendingMessages();
      
      if (pendingMessages.length > 0) {
        console.log(`Found ${pendingMessages.length} pending messages`);
        
        for (const message of pendingMessages) {
          await processMessage(message);
        }
      }
      
      setLastCheck(new Date());
    } catch (error) {
      console.error('Error checking messages:', error);
    } finally {
      setLoading(false);
    }
  };

  const getPendingMessages = async () => {
    try {
      const response = await fetch(`${syncServerUrl}/messages/pending`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      return data.messages || [];
    } catch (error) {
      console.error('Error fetching pending messages:', error);
      return [];
    }
  };

  const processMessage = async (message) => {
    try {
      console.log(`Processing message: ${message.message}`);
      
      // Get agent suggestions based on message content
      const suggestions = getAgentSuggestions(message.message);
      setAgentSuggestions(suggestions);
      
      // Auto-select agent if none specified
      let agentToUse = message.agent;
      if (!agentToUse && suggestions.length > 0) {
        agentToUse = Object.keys(AGENT_EXPERTS).find(key => AGENT_EXPERTS[key].name === suggestions[0].name);
      } else if (!agentToUse) {
        // Use random agent for variety
        const randomAgent = getRandomAgent();
        agentToUse = Object.keys(AGENT_EXPERTS).find(key => AGENT_EXPERTS[key].name === randomAgent.name);
      }
      
      // Generate response with Gemma 3n
      const response = await generateGemmaResponse(message.message, agentToUse);
      
      // Update the sync server with the response
      await updateMessageResponse(message.id, response);
      
      // Add to local messages
      setMessages(prev => [...prev, {
        ...message,
        response,
        agent: agentToUse,
        agentName: AGENT_EXPERTS[agentToUse]?.name || 'AI Assistant',
        agentEmoji: AGENT_EXPERTS[agentToUse]?.emoji || '🤖',
        status: 'completed',
        processedAt: new Date().toISOString(),
      }]);
      
    } catch (error) {
      console.error('Error processing message:', error);
      await updateMessageResponse(message.id, 'Error processing message', 'error');
    }
  };

  const generateGemmaResponse = async (message, agent) => {
    try {
      let prompt;
      
      if (agent && AGENT_EXPERTS[agent]) {
        // Use agent personality
        const agentData = AGENT_EXPERTS[agent];
        prompt = `${agentData.prompt}\n\nNow respond to this message: "${message}"\n\nRemember to stay in character as ${agentData.name} and use your unique personality and expertise.`;
      } else {
        // Default response
        prompt = `You are a helpful AI assistant. Respond to this message: "${message}". Keep your response concise and helpful.`;
      }
      
      const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemma-3n-e4b-it:generateContent?key=${apiKey}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          contents: [{
            parts: [{
              text: prompt
            }]
          }]
        }),
      });
      
      if (!response.ok) {
        throw new Error(`Gemini API error: ${response.status}`);
      }
      
      const data = await response.json();
      return data.candidates?.[0]?.content?.parts?.[0]?.text || 'No response generated';
      
    } catch (error) {
      console.error('Error generating Gemma response:', error);
      return 'Sorry, I encountered an error processing your request.';
    }
  };

  const updateMessageResponse = async (messageId, response, status = 'completed') => {
    try {
      const response2 = await fetch(
        `${syncServerUrl}/messages/${messageId}/response?response=${encodeURIComponent(response)}&status=${status}`,
        {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );
      
      if (!response2.ok) {
        throw new Error(`Update error: ${response2.status}`);
      }
      
      console.log(`Updated response for message ${messageId}`);
      
    } catch (error) {
      console.error('Error updating response:', error);
    }
  };

  const onRefresh = () => {
    checkForNewMessages();
  };

  const showAgentSelector = () => {
    setShowAgentModal(true);
  };

  const selectAgent = (agentKey) => {
    setSelectedAgent(agentKey);
    setShowAgentModal(false);
  };

  const sendMessage = async () => {
    if (!chatInput.trim()) return;

    try {
      // Generate response with Gemma 3n first
      const response = await generateGemmaResponse(chatInput.trim(), selectedAgent);
      
      // Add to local messages immediately
      const newMessage = {
        timestamp: new Date().toISOString(),
        type: 'user',
        message: chatInput.trim(),
        agent: selectedAgent || 'auto',
        response: response,
        agentName: selectedAgent ? AGENT_EXPERTS[selectedAgent]?.name || 'AI Assistant' : 'Auto-select',
        agentEmoji: selectedAgent ? AGENT_EXPERTS[selectedAgent]?.emoji || '🤖' : '🤖',
        status: 'completed',
        processedAt: new Date().toISOString(),
      };
      
      setMessages(prev => [...prev, newMessage]);
      setChatInput('');
      
      // Also send to local sync server for Streamlit
      try {
        await fetch(`${syncServerUrl}/messages`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            timestamp: new Date().toISOString(),
            type: 'user',
            message: chatInput.trim(),
            agent: selectedAgent || 'auto',
            response: response,
            status: 'completed'
          }),
        });
      } catch (syncError) {
        console.log('Local sync failed, but local response worked');
      }
      
      Alert.alert('Message Sent!', 'Your message has been processed by the multiverse! 🌌');
      
    } catch (error) {
      console.error('Error sending message:', error);
      Alert.alert('Error', 'Failed to send message. Please try again.');
    }
  };

  return (
    <View style={styles.container}>
      <SpaceBackground />
      <View style={styles.header}>
        <NeuralNet />
        <Text style={styles.title}>🧠🌌 Gemma 3n Multiverse ✨🔮</Text>
        <Text style={styles.subtitle}>🚀 Proactive Intelligence 🎯⚡</Text>
        
        <View style={styles.statusBar}>
          <View style={[styles.statusIndicator, { backgroundColor: isPolling ? '#4CAF50' : '#f44336' }]} />
          <Text style={styles.statusText}>
            {isPolling ? 'Polling Active' : 'Polling Stopped'}
          </Text>
        </View>
        
        {lastCheck && (
          <Text style={styles.lastCheck}>
            Last check: {lastCheck.toLocaleTimeString()}
          </Text>
        )}
      </View>

      <View style={styles.agentSelector}>
        <Text style={styles.agentLabel}>Select AI Agent:</Text>
        <View style={styles.agentDropdown}>
          <Text style={styles.agentDropdownText}>
            {selectedAgent ? AGENT_EXPERTS[selectedAgent]?.name || selectedAgent : 'Auto-select (Smart)'}
          </Text>
          <TouchableOpacity style={styles.agentButton} onPress={() => showAgentSelector()}>
            <Text style={styles.agentButtonText}>Change</Text>
          </TouchableOpacity>
        </View>
        {agentSuggestions.length > 0 && (
          <View style={styles.suggestionsContainer}>
            <Text style={styles.suggestionsLabel}>Suggested agents:</Text>
            {agentSuggestions.map((agent, index) => (
              <TouchableOpacity 
                key={index} 
                style={styles.suggestionItem}
                onPress={() => setSelectedAgent(Object.keys(AGENT_EXPERTS).find(key => AGENT_EXPERTS[key].name === agent.name))}
              >
                <Text style={styles.suggestionEmoji}>{agent.emoji}</Text>
                <Text style={styles.suggestionText}>{agent.name}</Text>
              </TouchableOpacity>
            ))}
          </View>
        )}
      </View>

      <ScrollView
        style={styles.messagesContainer}
        refreshControl={
          <RefreshControl refreshing={loading} onRefresh={onRefresh} />
        }
      >
        {messages.length === 0 ? (
          <View style={styles.emptyState}>
            <Text style={styles.emptyText}>No messages processed yet</Text>
            <Text style={styles.emptySubtext}>
              Messages from Streamlit will appear here
            </Text>
          </View>
        ) : (
          messages.map((msg, index) => (
            <View key={index} style={styles.messageCard}>
              <View style={styles.messageHeader}>
                <Text style={styles.messageType}>{msg.type}</Text>
                <Text style={styles.messageTime}>
                  {new Date(msg.timestamp).toLocaleTimeString()}
                </Text>
              </View>
              
              <Text style={styles.messageText}>{msg.message}</Text>
              
              {msg.agentName && (
                <View style={styles.agentInfo}>
                  <Text style={styles.agentEmoji}>{msg.agentEmoji}</Text>
                  <Text style={styles.agentText}>{msg.agentName}</Text>
                </View>
              )}
              
              {msg.response && (
                <View style={styles.responseContainer}>
                  <Text style={styles.responseLabel}>AI Response:</Text>
                  <Text style={styles.responseText}>{msg.response}</Text>
                </View>
              )}
              
              <View style={[styles.statusBadge, { backgroundColor: msg.status === 'completed' ? '#4CAF50' : '#f44336' }]}>
                <Text style={styles.statusBadgeText}>{msg.status}</Text>
              </View>
            </View>
          ))
        )}
      </ScrollView>

      <View style={styles.footer}>
        <TouchableOpacity style={styles.button} onPress={checkForNewMessages}>
          <Text style={styles.buttonText}>
            {loading ? 'Checking...' : 'Check Now'}
          </Text>
        </TouchableOpacity>
        
        <TouchableOpacity style={styles.button} onPress={checkForNewMessages}>
          <Text style={styles.buttonText}>Refresh</Text>
        </TouchableOpacity>
      </View>

      {/* Chat Input */}
      <View style={styles.chatInputContainer}>
        <TextInput
          style={styles.chatInput}
          placeholder="Type your message to the multiverse..."
          placeholderTextColor="#888888"
          value={chatInput}
          onChangeText={setChatInput}
          multiline
        />
        <TouchableOpacity style={styles.sendButton} onPress={sendMessage}>
          <Text style={styles.sendButtonText}>🚀</Text>
        </TouchableOpacity>
      </View>

      {/* Agent Selection Modal */}
      <Modal
        visible={showAgentModal}
        transparent={true}
        animationType="slide"
        onRequestClose={() => setShowAgentModal(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <Text style={styles.modalTitle}>🧠 Select AI Agent</Text>
            <Text style={styles.modalSubtitle}>Choose your multiverse guide:</Text>
            
            <FlatList
              data={[
                { key: null, name: 'Auto-select', emoji: '🤖', description: 'Smart selection' },
                ...Object.keys(AGENT_EXPERTS).map(key => ({
                  key,
                  ...AGENT_EXPERTS[key]
                }))
              ]}
              renderItem={({ item }) => (
                <TouchableOpacity
                  style={styles.agentOption}
                  onPress={() => selectAgent(item.key)}
                >
                  <Text style={styles.agentOptionEmoji}>{item.emoji}</Text>
                  <View style={styles.agentOptionText}>
                    <Text style={styles.agentOptionName}>{item.name}</Text>
                    <Text style={styles.agentOptionDescription}>{item.description}</Text>
                  </View>
                </TouchableOpacity>
              )}
              keyExtractor={(item, index) => item.key || index.toString()}
              style={styles.agentList}
            />
            
            <TouchableOpacity
              style={styles.modalCloseButton}
              onPress={() => setShowAgentModal(false)}
            >
              <Text style={styles.modalCloseText}>❌ Cancel</Text>
            </TouchableOpacity>
          </View>
        </View>
      </Modal>
    </View>
  );
}

const { width: screenWidth } = Dimensions.get('window');

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0F1419',
  },
  header: {
    backgroundColor: '#1E2A3A',
    padding: 20,
    paddingTop: 60,
    borderBottomWidth: 1,
    borderBottomColor: '#2D3F5F',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#4A90E2',
    textAlign: 'center',
  },
  subtitle: {
    fontSize: 14,
    color: '#7B68EE',
    textAlign: 'center',
    marginTop: 5,
  },
  statusBar: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 15,
  },
  statusIndicator: {
    width: 12,
    height: 12,
    borderRadius: 6,
    marginRight: 8,
  },
  statusText: {
    color: '#ffffff',
    fontSize: 14,
  },
  lastCheck: {
    color: '#888888',
    fontSize: 12,
    textAlign: 'center',
    marginTop: 5,
  },
  messagesContainer: {
    flex: 1,
    padding: 15,
  },
  emptyState: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 50,
  },
  emptyText: {
    color: '#ffffff',
    fontSize: 18,
    marginBottom: 10,
  },
  emptySubtext: {
    color: '#888888',
    fontSize: 14,
  },
  messageCard: {
    backgroundColor: '#1E2A3A',
    borderRadius: 10,
    padding: 15,
    marginBottom: 15,
    borderLeftWidth: 3,
    borderLeftColor: '#4A90E2',
  },
  messageHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 10,
  },
  messageType: {
    color: '#4A90E2',
    fontWeight: 'bold',
    textTransform: 'uppercase',
  },
  messageTime: {
    color: '#888888',
    fontSize: 12,
  },
  messageText: {
    color: '#ffffff',
    fontSize: 16,
    marginBottom: 10,
  },
  agentText: {
    color: '#7B68EE',
    fontSize: 12,
    marginBottom: 10,
  },
  responseContainer: {
    backgroundColor: '#2D3F5F',
    borderRadius: 8,
    padding: 10,
    marginBottom: 10,
  },
  responseLabel: {
    color: '#00CED1',
    fontSize: 12,
    fontWeight: 'bold',
    marginBottom: 5,
  },
  responseText: {
    color: '#ffffff',
    fontSize: 14,
  },
  statusBadge: {
    alignSelf: 'flex-start',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  statusBadgeText: {
    color: '#ffffff',
    fontSize: 10,
    fontWeight: 'bold',
  },
  footer: {
    flexDirection: 'row',
    padding: 15,
    backgroundColor: '#1E2A3A',
    borderTopWidth: 1,
    borderTopColor: '#2D3F5F',
  },
  button: {
    flex: 1,
    backgroundColor: '#4A90E2',
    padding: 15,
    borderRadius: 8,
    marginHorizontal: 5,
    alignItems: 'center',
  },
  buttonText: {
    color: '#ffffff',
    fontWeight: 'bold',
  },
  agentSelector: {
    backgroundColor: 'rgba(26, 35, 47, 0.8)',
    borderRadius: 10,
    padding: 15,
    marginBottom: 20,
    borderWidth: 1,
    borderColor: 'rgba(74, 144, 226, 0.3)',
  },
  agentLabel: {
    color: '#4A90E2',
    fontSize: 14,
    fontWeight: 'bold',
    marginBottom: 10,
  },
  agentDropdown: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: 'rgba(26, 35, 47, 0.8)',
    borderRadius: 8,
    padding: 12,
    borderWidth: 1,
    borderColor: 'rgba(74, 144, 226, 0.3)',
  },
  agentDropdownText: {
    color: '#ffffff',
    fontSize: 16,
  },
  agentButton: {
    backgroundColor: '#4A90E2',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 6,
  },
  agentButtonText: {
    color: '#ffffff',
    fontSize: 12,
    fontWeight: 'bold',
  },
  suggestionsContainer: {
    marginTop: 10,
  },
  suggestionsLabel: {
    color: '#7B68EE',
    fontSize: 12,
    marginBottom: 5,
  },
  suggestionItem: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(74, 144, 226, 0.1)',
    padding: 8,
    marginVertical: 2,
    borderRadius: 6,
  },
  suggestionEmoji: {
    fontSize: 16,
    marginRight: 8,
  },
  suggestionText: {
    color: '#ffffff',
    fontSize: 14,
  },
  agentInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(123, 104, 238, 0.1)',
    padding: 8,
    borderRadius: 6,
    marginBottom: 10,
  },
  agentEmoji: {
    fontSize: 16,
    marginRight: 8,
  },
  // Neural Net (Emoji Style)
  neuralNet: {
    position: 'absolute',
    top: 15,
    right: 15,
    zIndex: 10,
  },
  neuralText: {
    fontSize: 25,
    textAlign: 'center',
    textShadowColor: '#4A90E2',
    textShadowOffset: { width: 0, height: 0 },
    textShadowRadius: 10,
  },
  // Space Background (Emoji Universe)
  spaceContainer: {
    position: 'absolute',
    width: '100%',
    height: '100%',
    backgroundColor: 'transparent',
    zIndex: 0,
  },
  spaceEmoji: {
    position: 'absolute',
    opacity: 0.6,
    textShadowColor: '#ffffff',
    textShadowOffset: { width: 0, height: 0 },
    textShadowRadius: 3,
  },
  // Chat Input
  chatInputContainer: {
    flexDirection: 'row',
    padding: 15,
    backgroundColor: '#1E2A3A',
    borderTopWidth: 1,
    borderTopColor: '#2D3F5F',
    alignItems: 'flex-end',
  },
  chatInput: {
    flex: 1,
    backgroundColor: '#0F1419',
    color: '#ffffff',
    padding: 12,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: '#4A90E2',
    marginRight: 10,
    maxHeight: 100,
    fontSize: 16,
  },
  sendButton: {
    backgroundColor: '#4A90E2',
    width: 44,
    height: 44,
    borderRadius: 22,
    justifyContent: 'center',
    alignItems: 'center',
  },
  sendButtonText: {
    fontSize: 20,
  },
  // Agent Modal
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.8)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  modalContent: {
    backgroundColor: '#1E2A3A',
    borderRadius: 20,
    padding: 20,
    width: '90%',
    maxHeight: '80%',
    borderWidth: 2,
    borderColor: '#4A90E2',
  },
  modalTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#4A90E2',
    textAlign: 'center',
    marginBottom: 10,
  },
  modalSubtitle: {
    fontSize: 16,
    color: '#7B68EE',
    textAlign: 'center',
    marginBottom: 20,
  },
  agentList: {
    maxHeight: 400,
  },
  agentOption: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#0F1419',
    padding: 15,
    marginVertical: 5,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: '#2D3F5F',
  },
  agentOptionEmoji: {
    fontSize: 24,
    marginRight: 15,
  },
  agentOptionText: {
    flex: 1,
  },
  agentOptionName: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  agentOptionDescription: {
    color: '#888888',
    fontSize: 12,
    marginTop: 2,
  },
  modalCloseButton: {
    backgroundColor: '#f44336',
    padding: 15,
    borderRadius: 10,
    marginTop: 20,
    alignItems: 'center',
  },
  modalCloseText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: 'bold',
  },
});
